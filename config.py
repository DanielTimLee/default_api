import os

basedir = os.path.abspath(os.path.dirname(__file__))

HOST_API = os.environ['HOST_API']
HOST_CLIENT = os.environ['HOST_CLIENT']
# flask
SECRET_KEY = os.environ['SECRET_KEY']

# yagmail
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

# db
DATABASE_HOST = 'localhost:3306'
DATABASE_USERNAME = 'root'
DATABASE_PASSWORD = ''
DEFAULT_DATABASE = 'db_name'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{0}:{1}@{2}/{3}".format(DATABASE_USERNAME,
                                                                   DATABASE_PASSWORD,
                                                                   DATABASE_HOST,
                                                                   DEFAULT_DATABASE)

SQLALCHEMY_TRACK_MODIFICATIONS = True

TEMPLATES_AUTO_RELOAD = True
