from flask import Flask
import datetime, os, secrets
import pyrebase


config = {
    "apiKey": "AIzaSyBP0h6ejdqQKuy8SNikN-Eea4Ol8cTApM0",
    "authDomain": "applog-ee503.firebaseapp.com",
    "databaseURL": "https://applog-ee503.firebaseio.com",
    "projectId": "applog-ee503",
    "storageBucket": "applog-ee503.appspot.com",
    "messagingSenderId": "1075416798765",
    "appId": "1:1075416798765:web:a4dabf43fa5aaa075b0aa4",
    "measurementId": "G-TJGVC5CZ0P"
}

ID = "applogseed@gmail.com"
PW = "weapplog"


firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()
# user = auth.sign_in_with_email_and_password(ID, PW)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()

UPLOAD_FOLDER = '/static/img'
PHISICAL_ROOT = os.path.dirname( os.path.abspath( __file__ ) )

app = Flask(__name__)
# app.config.from_object("config.DevelopmentConfig")
app.config["SECRET_KEY"] = "superSecret"
app.config["UPLOAD_FOLDER"] = PHISICAL_ROOT + UPLOAD_FOLDER
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]

app.debug = True

from app import routes  
