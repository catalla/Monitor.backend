#
#	This file defines how the server responds to different
#	HTTP requests 
#


import json
import datetime
import random
from flask import request, abort
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_rest_service import app, api, mongo
from bson.objectid import ObjectId
from bson.json_util import dumps as Bdumps
from bson.json_util import loads as Bloads



# Period collection resources
def period_toggle(user):
  curDay = datetime.date.today().isoformat()

  # Check whether toggling on or off
  if user['cur_period'] == None:
    new_period = {
      "start": curDay,
      "end": None
    }
    # Update user's array of period info to include this new one
    pid = mongo.db.Periods.insert(new_period)
    user["periods"].append(pid)
    user["cur_period"] = pid
    mongo.db.Users.update({"username": user["username"]}, user)
    return user

  # If toggling off, you are adding the end to a period
  pid = user["cur_period"]
  period = mongo.db.Periods.find_one({"_id": pid})
  period["end"] = curDay

  # Check whether valid log
  if period_validate(user, period) == True:
    mongo.db.Periods.update({"_id": pid}, period)
    user["cur_period"] = None
    user = period_update_expectations(user, period)
    mongo.db.Users.update({"username": user["username"]}, user)

  # Period was 0 days, disregard entry
  else:
    mongo.db.Periods.remove({"_id": pid})
    user["cur_period"] = None
    user["periods"] = user["periods"][:-1]
    mongo.db.Users.update({"username": user["username"]}, user)
  return user



# Update expected values for duration and separation
def period_update_expectations(user, period):
  # Update expected length of period
  start = datetime.datetime.strptime(period["start"], "%Y-%m-%d")
  end = datetime.datetime.strptime(period["end"], "%Y-%m-%d")
  dur = end - start
  user["avg_len"] = (user["avg_len"]*user["len_sample"] + dur.days)/user["len_sample"]+1
  user["len_sample"] += 1

  # Update expected separation between periods
  if len(user["periods"]) >= 2:
    prev_pid = user["periods"][len(user["periods"])-2]
    prev_period = mongo.db.Periods.find_one({"_id": prev_pid})
    prev_start = datetime.datetime.strptime(prev_period["start"] , "%Y-%m-%d")
    diff = start - prev_start
    user["avg_sep"] = (user["avg_sep"]*user["sep_sample"] + diff.days)/user["sep_sample"]+1
    user["sep_sample"] += 1
  return user



# Attempt to filter out mistake logging
def period_validate(user, period):
  start = datetime.datetime.strptime(period["start"], "%Y-%m-%d")
  end = datetime.datetime.strptime(period["end"], "%Y-%m-%d")

  # Keep valid logs over 0 days
  diff = end - start
  return diff.days > 0



# Return next predicted period
def period_predict(user):
  if len(user["periods"]) < 1:
    return "na: You must log a period before prediction is enabled."

  # Look at most recent period start date to predict next start date
  last_pid = user["periods"][len(user["periods"])-1]
  last_period = mongo.db.Periods.find_one({"_id": last_pid})
  last_start = datetime.datetime.strptime(last_period["start"] , "%Y-%m-%d")

  # Prediction is based on user's current estimated period separation
  est_diff = datetime.timedelta(days=int(user["avg_sep"]))
  prediction = last_start + est_diff
  return datetime.datetime.strftime(prediction , "%Y-%m-%d")



# Return whether or not currently on period
def period_status(user):
  return user["cur_period"] != None



# Return what day of period, null if not on
def period_day(user):
  pid = user["cur_period"]
  if(pid == None):
      return -1
  period = mongo.db.Periods.find_one({"_id": pid})
  start = datetime.datetime.strptime(period["start"], "%Y-%m-%d")
  curDay = datetime.date.today()
  # return num of days
  diff = (curDay - start)+1
  return diff.days



# Log today's mood
def stats_mood(user, mood):
  day = stats_update_status(user)
  day["stats"]["mood"] = (day["stats"]["mood"]*day["cnt_mood"] + int(mood))/day["cnt_mood"]+1
  day["cnt_mood"] += 1
  mongo.db.Stats.update({"date": curDay, "username": user["username"]}, day)
  return True



# Log today's sensor data
def stats_sensor(user, sensor):
  day = stats_update_status(user)
  temp = float(sensor[:sensor.find(",")])
  heart = float(sensor[sensor.find(",")+1:])

  # Keep moving avg on temp for the day
  day["stats"]["temp"] = (day["stats"]["temp"]*day["cnt_temp"] + temp)/day["cnt_temp"]+1
  day["cnt_temp"] += 1

  # Keep moving avg on heart rate for the day
  day["stats"]["heart"] = (day["stats"]["heart"]*day["cnt_heart"] + heart)/day["cnt_heart"]+1
  day["cnt_heart"] += 1

  mongo.db.Stats.update({"date": curDay, "username": user["username"]}, day)
  return True



# Create a stats entry for the day if not already done
def stats_create_day(user, day):
  new_day = {
    "username": user["username"],
    "date": day,
    "stats": {
      "date": day,
      "period": False,
      "mood": 5,
      "heart": 60,
      "temp": 33
    },
    "cnt_mood": 0,
    "cnt_heart": 0,
    "cnt_temp": 0
  }
  mongo.db.Stats.insert(new_day)
  return True



# Check current period status, update in stats doc
def stats_update_status(user):
  curDay = datetime.date.today().isoformat()
  if not mongo.db.Stats.find_one({"date": curDay, "username": user["username"]}):
    stats_create_day(user, curDay)
  day = mongo.db.Stats.find_one({"date": curDay, "username": user["username"]})
  day['stats']['period'] = period_status
  return day



# Return dump of all stats for this user
def stats_get_all(user):
  for day in mongo.db.Stats.find({"date": curDay, "username": user["username"]}):
    print "todo"
  return 1



# Return dump of stats in date range for this user
def stats_get_range(user):
  return 1



# Return the date of the previous period start
def period_prev(user):
  if len(user["periods"]) < 1:
    return "na: You must log a period before viewing past information."

  # Look at most recent period start date to predict next start date
  last_pid = user["periods"][len(user["periods"])-1]
  last_period = mongo.db.Periods.find_one({"_id": last_pid})
  last_start = last_period["start"]
  last_end = last_period["end"]
  return (last_start + " - " + last_end)
  


# Return a tip if period is one or two days away
def user_tip(user):
  if user["days_until"] > 2:
    return "na: Tips are generated within days of predicted period"
  tips = ["Avoid salty foods such as chips in the week before your period", "Avoid sugary foods such as candy in the week before your period", "Avoid coffee, black tea, and other caffeine sources in the week before your period", "To reduce cramps, try gentle exercise, such as walking or swimming", "Regular exercise reduces period pain. Try joining a sports team!", "Dark chocolate may reduce menstrual cramping", "Make sure to stay hydrated, especially in the days during and before your period", "Avoid alcohol before and during your period", "Take ibuprofen the night before your period starts, to keep cramping to a minimum", "Menstrual pain? Try using a heating pad on your abdomen", "Raspberry leaf herbal tea can reduce cramping", "Take a hot bath to destress and reduce pain", "To keep blood sugar levels consistent, eat smaller meals more frequently rather than a few large meals", "Get plenty of sleep - around 8 hours - to reduce stress and other PMS symptoms", "Stress worsens PMS symptoms, so find your own source of stress relief, such as writing in a journal"]
  return tips[random.randint(0,len(tips)-1)]
  


# Use this to give the controller user information based on username
class Users(restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()

        # ******************
        # Flags definitions
        self.parser.add_argument('toggle', type=str, required=False)
        self.parser.add_argument('predict', type=str, required=False) 
        self.parser.add_argument('status', type=str, required=False) 
        self.parser.add_argument('day', type=str, required=False)
        self.parser.add_argument('tip', type=str, required=False)
        self.parser.add_argument('prev', type=str, required=False)
        self.parser.add_argument('get_range', type=str, required=False)
        self.parser.add_argument('get_all', type=str, required=False)
        self.parser.add_argument('sensor', type=str, required=False)
        self.parser.add_argument('mood', type=str, required=False)

        super(Users, self).__init__()

    # Get user info or create new user
    def get(self, username):
        # Make user if not pre-existing
        pre_exist = mongo.db.Users.find_one({"username": username})
        if pre_exist == None:
          new_user = {
              "username": username,
              "periods": [],
              "cur_period": None,
              "avg_sep": 28,
              "sep_sample": 1,
              "avg_len": 4,
              "len_sample": 1,
              "days_until": 28
            }
          # Return user info
          mongo.db.Users.insert(new_user)
          return mongo.db.Users.find_one({"username": username})

        # Update status of days until period
        if period_predict(pre_exist)[0:3] != 'na:':
          next_start = datetime.datetime.strptime(period_predict(pre_exist), "%Y-%m-%d")
          curDay = datetime.datetime.today()
          pre_exist['days_until'] = (next_start - curDay).days
          mongo.db.Users.update({"username": username}, pre_exist)

        # Return pre_existing user info
        return pre_exist

    # Either invoke toggle or predict next
    def post(self, username):
        # Parse args
        args = self.parser.parse_args()
        nargs = len(args) - sum([args[x]==None for x in args])
        if nargs > 1:
          return None

        # Get user info to edit
        user = self.get(username)

        if args['toggle'] != None:
          return period_toggle(user)
        if args['predict'] != None:
          return period_predict(user)
        if args['status'] != None:
          return period_status(user)
        if args['day'] != None:
          return period_day(user)
        if args['tip'] != None:
          return user_tip(user)
        if args['prev'] != None:
          return period_prev(user)
        if args['get_range'] != None:
          return stats_get_range(user)
        if args['get_all'] != None:
          return stats_get_all(user)
        if args['mood'] != None:
          return stats_mood(user, args['mood'])
        if args['sensor'] != None:
          return stats_sensor(user, args['sensor'])
        else:
          return None


# Return status information about the server
class Root(restful.Resource):
    def get(self):
        return {
            'status': 'OK',
            'oneweek': 'winners',
            'Best Coders': 'Jesse and Chad',
            'mongo': str(mongo.db),
        }

api.add_resource(Root, '/')
api.add_resource(Users, '/users/<username>')
