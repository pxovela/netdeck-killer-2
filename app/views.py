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

# session secret key
app.secret_key = 'dljsaklqka24e21cjn!Ew@@dsa5'

#list of all current decks
deck_details = pd.read_csv('app/static/deck_details.csv')

def filter_decks(selected_champs):
   if len(selected_champs) == 6:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs))]
   elif len(selected_champs) == 5:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs))]
   elif len(selected_champs) == 4:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs))]
   elif len(selected_champs) == 3:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'] == "None")]
   elif len(selected_champs) == 2:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'] == "None") & (deck_details['champion_4'] == "None")]
   elif len(selected_champs) == 1:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'] == "None") & (deck_details['champion_3'] == "None") & (deck_details['champion_4'] == "None")]
   elif len(selected_champs) == 0:
      return deck_details[(deck_details['champion_1']=='None') & (deck_details['champion_2']=='None') & (deck_details['champion_3']=="None") & (deck_details['champion_4']=="None")]

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
      # get the list of filtered champs
      filtered_champions = session.get("filtered_champions", None)
      # check if user selected more than 6 champs and deal with it
      if len(request.form.getlist('champion_check')) > 6:
         champ_error = "Please select less than 6 champions!"
         return render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions, champ_error=champ_error)
      # if no issues with champs, load initial game view with starting values
      else:
         # get list of selected champs
         selected_champions = request.form.getlist('champion_check')
         session["selected_champions"] = selected_champions
         # filter possible decks by selected champions
         potential_decks = filter_decks(selected_champions)
         print(potential_decks)
         #set initial values for mana and spell mana
         session['mana'] = 1
         mana = session.get("mana", None)
         session['spell_mana'] = 0
         spell_mana = session.get("spell_mana", None)
         print(selected_champions)
         return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana)

@app.route('/game_update', methods=['GET', 'POST'])
def game_update():
   # update mana values
   session['mana'] = request.form.get('mana')
   mana = session.get("mana", None)
   session['spell_mana'] = request.form.get('spell_mana')
   spell_mana = session.get("spell_mana", None)
   print(request.form.get('mana'))
   filtered_champions=session.get("filtered_champions",None)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana)

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