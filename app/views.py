# import app variable
from app import app
# import render template function
from flask import render_template, session
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
# import card @staticmethod
from app import add_cards as cards
from io import StringIO
import pandas as pd
import json

#list of all champs and regions
regions = ['Bilgewater', 'Demacia', 'Freljord', 'Ionia', 'Noxus', 'Piltover & Zaun', 'Shadow Isles']

app.secret_key = 'dljsaklqka24e21cjn!Ew@@dsa5'

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
         selected_regions = request.form.getlist('region_check')
         #filter champions based on selected regions
         filtered_champions = cards.champions[cards.champions['region'].isin(selected_regions)]
         # removed duplicate champts due to leveled up cards
         filtered_champions = filtered_champions[~filtered_champions['cardCode'].str.contains('T')]
         # Turned dataframe into json
         filtered_champions = json.loads(filtered_champions.to_json(orient='records'))
         session["filtered_champions"]=filtered_champions
         render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions)
   return render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions)

@app.route('/game', methods=['GET', 'POST'])
def game():
   if request.method == 'POST':
      filtered_champions=session.get("filtered_champions",None)
      if len(request.form.getlist('champion_check')) > 6:
         champ_error = "Please select less than 6 champions!"
         return render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions, champ_error=champ_error)
      else:
         selected_champions = request.form.getlist('champion_check')
         session["selected_champions"]=selected_champions
         print(selected_champions)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions)

@app.route('/game_update', methods=['GET', 'POST'])
def game_update():
   print(request.form.get('mana'))
   filtered_champions=session.get("filtered_champions",None)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions)

req = ''
opponent_played=set([])
@app.route('/api', methods=['GET','POST'])
def api():
   if request.data:
      req = json.loads(request.data)
      current_cards = req['Rectangles']
      current_cards = [x for x in current_cards if str(x['LocalPlayer']) == 'False' and str(x['CardCode']) != 'face']
      for card in current_cards:
         opponent_played.add(card['CardCode'])
      print(opponent_played)
      filtered_champions=session.get("filtered_champions",None)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions)