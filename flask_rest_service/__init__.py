import os
from flask import Flask
from flask.ext import restful
from flask.ext.pymongo import PyMongo
from flask import make_response
from bson.json_util import dumps

# URL of Mongo Database
MONGO_URL = 'mongodb://monitor_client:1week1@ds029705.mlab.com:29705/heroku_s4pxkw3j'

app = Flask(__name__)

# Launch pyMongo instance
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

# Converts BSON return type to json output type
def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

# Sets what displays on the server if you visit in browser
DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api = restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS

import flask_rest_service.resources
