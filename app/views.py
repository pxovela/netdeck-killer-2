# import app variable
from app import app
# import render template function
from flask import render_template
# import datetime
from datetime import datetime
#import request and redirect
from flask import request, redirect
# import to send back json respons
from flask import jsonify, make_response
# os library
import os
# library to secure filenames
from werkzeug.utils import secure_filename

# create a main view
@app.route('/')
def index():
   return render_template("public/killer-index.html")