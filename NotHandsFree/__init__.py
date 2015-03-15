import os
import redis
from flask import Flask
from flask_sockets import Sockets
from flask.ext.heroku import Heroku
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

app = Flask(__name__)

heroku = Heroku()
heroku.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['REDIS_URL'] = os.environ['REDISTOGO_URL']
app.config['REDIS_CHAN'] = "nothandsfree"

app.config['TWILIO_ACCOUNT_SID'] = os.environ['TWILIO_ACCOUNT_SID']
app.config['TWILIO_AUTH_TOKEN'] = os.environ['TWILIO_AUTH_TOKEN']
app.config['TWILIO_CALLER_ID'] = os.environ['TWILIO_CALLER_ID']
app.config['TWILIO_API_PROXY'] = os.environ['TWILIO_API_PROXY']

sentry = Sentry(app)
redis = redis.from_url(app.config['REDIS_URL'])
db = SQLAlchemy(app)
sockets = Sockets(app)

from NotHandsFree.ws import Backend
backend = Backend()
backend.start()

from NotHandsFree import views