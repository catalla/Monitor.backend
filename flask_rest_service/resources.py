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

# Make one class for each type of major request
class Emotions(restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()

        # Define what arguments to take for a new emotion entry
        self.parser.add_argument('uid', type=str, required=True)
        self.parser.add_argument('mood', type=str, required=True)
        super(Emotions, self).__init__()

    # Return all collection entries
    def get(self):
        return [x for x in mongo.db.Emotions.find()]

    # Add a new emotion entry
    def post(self):
        args = self.parser.parse_args()

      	curTime = datetime.datetime.now().isoformat()

        # Check whether updating or inserting
        # If the document already exists, update it
        if (mongo.db.Emotions.find_one({"uid": args["uid"]}) != None):
            emotion_journal = (mongo.db.Emotions.find_one({"uid": args["uid"]}))
            emotion_journal["emotions"].append((args["mood"], curTime))
            mongo.db.Emotions.update({"uid": args["uid"]}, emotion_journal)

        else:
            new_entry = {
              "uid":      args["uid"],
              "emotions": [(args["mood"], curTime),]
            }
            mongo.db.Emotions.insert(new_entry)

        return mongo.db.Emotions.find_one_or_404({"uid": args["uid"]})["_id"]


# Use this to give the controller user information based on user ID
class UserInfo(restful.Resource):
    def get(self, user_id):
        return mongo.db.Users.find_one_or_404({"_id": user_id})


class Register(restful.Resource):
    """Register a new user in the database.
    user = {
    "username":
    "password":
    }
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()

        # Define what arguments to take for a new user
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)

    def get(self):
        return [x for x in mongo.db.Users.find()]

    def post(self):
        args = self.parser.parse_args()

        if (mongo.db.Users.find_one({"username": args['username']}) != None):
            return "Username is already taken!"

        user = {
            'username': args['username'],
            'password': args['password'],
            'emotions_id': 'none',
            'periods_id': 'none'
        }

        return {
            "_id": mongo.db.Users.insert(user),
        }

class Login(restful.Resource):
    """Check if user is in the database, if it is, then log in.
    username = string
    password = string
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()

        # Define what arguments to take for a new apartment
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)
        super(Login, self).__init__()

    def get(self):
        return [x for x in mongo.db.Users.find()]

    def post(self):
        args = self.parser.parse_args()

        user = mongo.db.Users.find_one({"username": args['username']})
        if user:
            if user["password"] == args['password']:
                return user
            else:
                return "Password is incorrect"

        else:
            return "User not found"


# Return status information about the server
class Root(restful.Resource):
    def get(self):
        return {
            'status': 'OK',
            'oneweek': 'winners',
            'mongo': str(mongo.db),
        }

api.add_resource(Root, '/')
api.add_resource(Emotions, '/emotions/')
api.add_resource(Register, '/register/')
api.add_resource(Login, '/login/')
api.add_resource(UserInfo, '/users/<ObjectId:user_id>')
