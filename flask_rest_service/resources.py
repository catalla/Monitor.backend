#
#	This file defines how the server responds to different
#	HTTP requests 
#


import json
import datetime
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
      "end:": None
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
  if period_validate(user, period) != None:
    mongo.db.Periods.update({"_id": pid}, period)
    user["cur_period"] = None
    user = period_update_expectations(user, period)
    mongo.db.Users.update({"username": user["username"]}, user)

  # Period was 0 days, disregard entry
  else:
    mongo.db.Periods.remove({"_id": pid})
    user["cur_period"] = None
    user["periods"].remove(pid)
    mongo.db.Users.update({"username": user["username"]}, user)
  return user



# Update expected values for duration and separation
def period_update_expectations(user, period):
  # Update expected length of period
  start = datetime.datetime.strptime(period["start"], "%Y-%m-%d")
  end = datetime.datetime.strptime(period["end"], "%Y-%m-%d")
  dur = end - start
  user["avg_len"] =
    (user["avg_len"]*user["len_sample"] + dur)/user["len_sample"]+1
  user["len_sample"] += 1

  # Update expected separation between periods
  if len(user["periods"]) >= 2:
    prev_pid = user["periods"][len(user["periods"])-2]
    prev_period = mongo.db.Periods.find_one({"_id": last_pid})
    prev_start = datetime.datetime.strptime(last_period["start"] , "%Y-%m-%d")
    diff = start - prev_start
    user["avg_sep"] =
    (user["avg_sep"]*user["sep_sample"] + dur)/user["sep_sample"]+1
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
    return "You must log a period before prediction is enabled."

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
  period = mongo.db.Periods.find_one({"_id": pid})
  if(period["end"] != None):
      return None
  start = datetime.datetime.strptime(period["start"], "%Y-%m-%d")
  curDay = datetime.date.today().isoformat()
  end = datetime.datetime.strptime(curDay, "%Y-%m-%d")

  # Keep valid logs over 0 days
  diff = end - start
  return diff



# Log today's mood
def stats_mood(user):




# Use this to give the controller user information based on username
class Users(restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()

        # ******************
        # Flags definitions
        self.parser.add_argument('toggle', type=str, required=False)
        self.parser.add_argument('predict', type=str, required=False) 
        self.parser.add_argument('status', type=str, required=False) 
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
              "len_sample": 1
            }
          # Return user info
          mongo.db.Users.insert(new_user)
          return mongo.db.Users.find_one({"username": username})

        # Return pre_existing user info
        return pre_exist

    # Either invoke toggle or predict next
    def post(self, username):
        # Parse args
        args = self.parser.parse_args()
        nargs = len(args) - sum([args[x]==None for x in args])
        if nargs > 1:
          return "Select exactly one option"

        # Get user info to edit
        user = self.get(username)

        if args['toggle'] != None:
          return period_toggle(user)
        if args['predict'] != None:
          return period_predict(user)
        if args['status'] != None:
          return period_status(user)
        else:
          return "Internal Server Error: Could not parse args"


# Return status information about the server
class Root(restful.Resource):
    def get(self):
        return {
            'status': 'OK',
            'oneweek': 'winners',
            'mongo': str(mongo.db),
        }

api.add_resource(Root, '/')
api.add_resource(Users, '/users/<username>')
