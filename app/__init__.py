# import flask
from flask import Flask


# set app variable
app = Flask(__name__)

if app.config["ENV"] == "production":
   app.config.from_object("config.ProductionConfig")
else:
   app.config.from_object("config.DevelopmentConfig")

print(f'ENV is set to: {app.config["ENV"]}')

# allow multiple python files import
from app import views