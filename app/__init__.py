from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.models import *

db.create_all()

from flask_restful import Api

api_root = Api(app)

from flask_oauthlib.provider import OAuth2Provider

oauth_provider = OAuth2Provider(app)

import logging
import sys

oauth_logger = logging.getLogger('oauthlib')
oauth_logger.addHandler(logging.StreamHandler(sys.stdout))
oauth_logger.setLevel(logging.DEBUG)


from app.routes import *
from app.api import *
