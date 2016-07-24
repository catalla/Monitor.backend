#
#	This file defines how the server responds to different
#	HTTP requests 
#


import json
from flask import request, abort
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_rest_service import app, api, mongo
from bson.objectid import ObjectId
from bson.json_util import dumps as Bdumps
from bson.json_util import loads as Bloads

# Make one class for each type of major request
class TODO(restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()

        # Define what arguments to take for a new doc
        self.parser.add_argument('TODO', type=str, required=True)
        super(className, self).__init__()

    # Return all collection documents
    def get(self):
        return [x for x in mongo.db.TODOCollection.find()]

    # Add a new doc
    def post(self):
        args = self.parser.parse_args()

        # Create json object from the arguments and add to DB
        jo = json.loads(args['TODOargname'])

        # Check whether updating or inserting
        # If the document already exists, update it
        if (mongo.db.TODOcollname.find_one({"name": jo["name"]}) != None):
            TODOex_id = (mongo.db.TODOex.find_one({"name": jo["name"]})) ["_id"]
            mongo.db.TODOcoll.update({"_id": TODOex_id}, jo)

        else:
            TODOex_id = mongo.db.TODOCOll.insert(jo)

        return mongo.db.TODOcoll.find_one({"_id": TODOex_id})


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

        # Define what arguments to take for a new apartment
        self.parser.add_argument('username', type=str, required=True)
        self.parser.add_argument('password', type=str, required=True)
        self.parser.add_argument('phonenum', type=str, required=True)

    def get(self):
        return [x for x in mongo.db.Users.find()]

    def post(self):
        args = self.parser.parse_args()

        if (mongo.db.Users.find_one({"username": args['username']}) != None):
            return "Username is already taken!"

        user = {
            'username': args['username'],
            'password': args['password'],
            'workload': 0,
            'tasks': [],
            'phonenum': args['phonenum'],
        }

        response = {"validation_code": "000000"} 
        if (mongo.db.Users.find_one({"phonenum": args['phonenum']}) == None):
            try:
                response = twilio_client.caller_ids.validate(args['phonenum'])
            except:
                response = {"validation_code": "000000"}
                print "User did not validate phone number!"

        return {
            "_id": mongo.db.Users.insert(user),
            "confirm": response['validation_code'],
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
api.add_resource(ApartmentList, '/TODO_ex/')
api.add_resource(Task, '/tasks/<ObjectId:TODO_ex_id>')
api.add_resource(Register, '/register/')
api.add_resource(Login, '/login/')
api.add_resource(UserInfo, '/users/<ObjectId:user_id>')
