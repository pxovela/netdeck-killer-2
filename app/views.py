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

#list of all champs and regions
regions = ['Bilgewater', 'Demacia', 'Freljord', 'Ionia', 'Noxus', 'Piltover & Zaun', 'Shadow Isles']

# create a main view
@app.route('/')
def index():
   return render_template("public/killer-index.html")

# route for region select
@app.route('/region_select')
def region_select():
   return render_template("public/region-select.html", regions=regions)

# route for region select
@app.route('/champion_select', methods=['GET', 'POST'])
def champion_select():
   if request.method == 'POST':
      if len(request.form.getlist('region_check'))==0:
         region_error = "Select at least 1 region!"
         return render_template("public/region-select.html", regions=regions, region_error=region_error)
      elif len(request.form.getlist('region_check')) > 2:
         region_error = "You can select no more than TWO regions!"
         return render_template("public/region-select.html", regions=regions, region_error=region_error)
      else:
         render_template("public/champion-select.html", regions=regions)
   return render_template("public/champion-select.html", regions=regions)