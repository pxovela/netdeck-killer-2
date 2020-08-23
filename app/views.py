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
from lor_deckcodes import LoRDeck, CardCodeAndCount
import scipy.stats as ss
import numpy as np

#list of all champs and regions
regions = ['Bilgewater', 'Demacia', 'Freljord', 'Ionia', 'Noxus', 'Piltover & Zaun', 'Shadow Isles']

# session secret key
app.secret_key = 'dljsaklqka24e21cjn!Ew@@dsa5'

#list of all current decks
deck_details = pd.read_csv('app/static/deck_details.csv')


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
      session.clear()
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
         filtered_champions = filtered_champions[['name', 'cardCode']]
         filtered_champions.sort_values(by=['name'], inplace=True)
         filtered_champions = json.loads(filtered_champions.to_json(orient='records'))
         session["filtered_champions"] = filtered_champions
         session["selected_regions"] = selected_regions
         render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions)
   return render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions)

# function to filter decks -- Probably can do something shorter than this mess
def filter_decks(selected_champs):
   selected_regions = session.get("selected_regions", None)
   if len(selected_champs) == 6:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs)) & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 5:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs)) & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 4:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'].isin(selected_champs)) & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 3:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'].isin(selected_champs)) & (deck_details['champion_4'] == "None") & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 2:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'].isin(selected_champs)) & (deck_details['champion_3'] == "None") & (deck_details['champion_4'] == "None") & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 1:
      return deck_details[(deck_details['champion_1'].isin(selected_champs)) & (deck_details['champion_2'] == "None") & (deck_details['champion_3'] == "None") & (deck_details['champion_4'] == "None") & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]
   elif len(selected_champs) == 0:
      return deck_details[(deck_details['champion_1']=='None') & (deck_details['champion_2']=='None') & (deck_details['champion_3']=="None") & (deck_details['champion_4']=="None") & (deck_details['region_1'].isin(selected_regions)) & (deck_details['region_2'].isin(selected_regions))]

# function to calculate weighted average card counts
def wavg(group, avg_name, weight_name):
    d = group[avg_name]
    w = group[weight_name]
    try:
        return (d * w).sum() / w.sum()
    except ZeroDivisionError:
        return d.mean()

# function to caclulate min probability
def draw_min(group, copies, round_num, target):
   no_mul = 4  # Number of draws
   round_n = round_num
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(target)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(target)
   return float(1 - mull_prob_0 * round_prob_0)

def draw_max(group, copies, round_num, target):
   no_mul = 8  # Number of draws
   round_n = round_num
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(target)
   round_prob_0 = ss.hypergeom(40, copies, round_n).pmf(target)
   return float(1 - mull_prob_0 * round_prob_0)

def draw_min_1(group, copies, round_num):
   no_mul = 4  # Number of draws
   round_n = round_num
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_1 = ss.hypergeom(36, copies, round_n).pmf(1)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)
   return float( mull_prob_0*round_prob_1 + mull_prob_1*round_prob_0)

def draw_max_1(group, copies, round_num):
   no_mul = 8  # Number of draws
   round_n = round_num
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_1 = ss.hypergeom(36, copies, round_n).pmf(1)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)
   return float(mull_prob_0 * round_prob_1 + mull_prob_1 * round_prob_0)
   
def draw_min_2(group, copies, round_num):
   no_mul = 4  # Number of draws
   round_n = round_num

   rounded_copies = np.where(group[copies] - 1 > 0, round(group[copies] - 1), 0)
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_2 = ss.hypergeom(36, copies, round_n).pmf(2)

   mull_prob_2 = ss.hypergeom(40, copies, no_mul).pmf(2)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_1 = ss.hypergeom(36, rounded_copies, round_n).pmf(1)
   return float( mull_prob_0*round_prob_2 + mull_prob_2*round_prob_0 + mull_prob_1*round_prob_1)

def draw_max_2(group, copies, round_num):
   no_mul = 8  # Number of draws
   round_n = round_num
  
   rounded_copies = np.where(group[copies] - 1 > 0, round(group[copies] - 1), 0)
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_2 = ss.hypergeom(36, copies, round_n).pmf(2)

   mull_prob_2 = ss.hypergeom(40, copies, no_mul).pmf(2)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_1 = ss.hypergeom(36, rounded_copies, round_n).pmf(1)
   return float(mull_prob_0 * round_prob_2 + mull_prob_2 * round_prob_0 + mull_prob_1 * round_prob_1)
   
def draw_min_3(group, copies, round_num):
   no_mul = 4  # Number of draws
   round_n = round_num

   rounded_copies = np.where(group[copies] - 1 > 0, group[copies] - 1, 0)
   rounded_copies_2 = np.where(group[copies] - 2 > 0, round(group[copies] - 2), 0)
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_3 = ss.hypergeom(36, round(copies), round_n).pmf(3)

   mull_prob_3 = ss.hypergeom(40, round(copies), no_mul).pmf(3)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_2 = ss.hypergeom(36, rounded_copies, round_n).pmf(2)

   mull_prob_2 = ss.hypergeom(40, copies, no_mul).pmf(2)
   round_prob_1 = ss.hypergeom(36, rounded_copies_2, round_n).pmf(1)
   return float( mull_prob_0*round_prob_3 + mull_prob_3*round_prob_0 + mull_prob_1*round_prob_2 + mull_prob_2*round_prob_1)

def draw_max_3(group, copies, round_num):
   no_mul = 8  # Number of draws
   round_n = round_num

   rounded_copies = np.where(group[copies] - 1 > 0, group[copies] - 1, 0)
   rounded_copies_2 = np.where(group[copies] - 2 > 0, round(group[copies] - 2), 0)
   copies = group[copies]
   mull_prob_0 = ss.hypergeom(40, copies, no_mul).pmf(0)
   round_prob_3 = ss.hypergeom(36, round(copies), round_n).pmf(3)

   mull_prob_3 = ss.hypergeom(40, round(copies), no_mul).pmf(3)
   round_prob_0 = ss.hypergeom(36, copies, round_n).pmf(0)

   mull_prob_1 = ss.hypergeom(40, copies, no_mul).pmf(1)
   round_prob_2 = ss.hypergeom(36, rounded_copies, round_n).pmf(2)

   mull_prob_2 = ss.hypergeom(40, copies, no_mul).pmf(2)
   round_prob_1 = ss.hypergeom(36, rounded_copies_2, round_n).pmf(1)
   return float( mull_prob_0*round_prob_3 + mull_prob_3*round_prob_0 + mull_prob_1*round_prob_2 + mull_prob_2*round_prob_1)



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
         if potential_decks.empty:
            champ_error = "No deck info available on selected champions!"
            print(champ_error)
            return render_template("public/champion-select.html", regions=regions, filtered_champions=filtered_champions, champ_error=champ_error)
         else:
            #total_matches = potential_decks['matches_played'].sum()
            deck_count = str(potential_decks['deck_code'].count())
            session["deck_count"] = deck_count
            df = []
            for index, row in potential_decks.iterrows():
               deck = LoRDeck.from_deckcode(row['deck_code'])
               #iterate through each card of the deck
               for card in deck.cards:
                  d = {
                        'cardCode' : card.card_code,
                        'count': card.count,
                        'matches_played': row['matches_played']
                  }
                  df.append(d)
            combined_deck = pd.DataFrame(df)
            # add up the same card numbers
            combined_deck_counts = combined_deck[['cardCode', 'count', 'matches_played']].groupby(['cardCode', 'count']).sum()
            combined_deck_counts = combined_deck_counts.reset_index()
            # calculate matches per card
            combined_cards = combined_deck[['cardCode', 'matches_played']].groupby(['cardCode']).sum()
            # calculate weighted average of card counts
            combined_cards['weighted_cards'] = round(combined_deck_counts.groupby(['cardCode']).apply(wavg, 'count', 'matches_played'), 2)
            # calculate draw probability
            combined_cards.reset_index(level=0, inplace=True)
            session['round_n'] = 1
            round_n = session.get("round_n", None)

            combined_cards['draw_min'] = combined_cards.groupby(['cardCode']).apply(draw_min, 'weighted_cards', round_n, 0).reset_index()[0]
            combined_cards['draw_max'] = combined_cards.groupby(['cardCode']).apply(draw_max, 'weighted_cards', round_n, 0).reset_index()[0]

            combined_cards['draw_min_1'] = combined_cards.groupby(['cardCode']).apply(draw_min_1, 'weighted_cards', round_n).reset_index()[0]
            combined_cards['draw_max_1'] = combined_cards.groupby(['cardCode']).apply(draw_max_1, 'weighted_cards', round_n).reset_index()[0]

            combined_cards['draw_min_2'] = combined_cards.groupby(['cardCode']).apply(draw_min_2, 'weighted_cards', round_n).reset_index()[0]
            combined_cards['draw_max_2'] = combined_cards.groupby(['cardCode']).apply(draw_max_2, 'weighted_cards', round_n).reset_index()[0]
            #print(1- ((1-combined_cards['draw_min']) + combined_cards['draw_min_1']+combined_cards['draw_min_2']))
            combined_cards['draw_min_3'] = 1- ((1-combined_cards['draw_min']) + combined_cards['draw_min_1']+combined_cards['draw_min_2'])
            combined_cards['draw_max_3'] = 1- ((1-combined_cards['draw_max']) + combined_cards['draw_max_1']+combined_cards['draw_max_2'])
            # join card details like mana cost, etc
            combined_cards = combined_cards.join(cards.all_cards.set_index('cardCode'), on='cardCode', how='left')
            combined_cards.reset_index(level=0, inplace=True, drop=True)
            combined_cards.sort_values(by=['cost'], inplace=True)
            # calculate deck probability of each card
            combined_cards['deck_chance'] = combined_cards['matches_played'] / potential_decks['matches_played'].sum()
            # caclulate chance of having a card based on probabilty of drawing it + a chance to have the card in the deck
            combined_cards['chance_min'] = combined_cards['deck_chance'] * combined_cards['draw_min'] * 100
            combined_cards['chance_max'] = combined_cards['deck_chance'] * combined_cards['draw_max'] * 100

            combined_cards['chance_min_1'] = combined_cards['deck_chance'] * (combined_cards['draw_min_1']) * 100
            combined_cards['chance_max_1'] = combined_cards['deck_chance'] * (combined_cards['draw_max_1']) * 100

            combined_cards['chance_min_2'] = combined_cards['deck_chance'] * (combined_cards['draw_min_2']) * 100
            combined_cards['chance_max_2'] = combined_cards['deck_chance'] * (combined_cards['draw_max_2']) * 100

            combined_cards['chance_min_3'] = combined_cards['deck_chance'] * (combined_cards['draw_min_3']) * 100
            combined_cards['chance_max_3'] = combined_cards['deck_chance'] * (combined_cards['draw_max_3']) * 100

            combined_cards['chance_min_0'] = combined_cards['deck_chance'] * (1 - combined_cards['draw_max']) * 100
            combined_cards['chance_max_0'] = combined_cards['deck_chance'] * (1 - combined_cards['draw_min']) * 100
            # format numbers to be displayed properly
            combined_cards['chance_string'] = combined_cards['chance_min'].round().astype(int).astype(str) + '-' + combined_cards['chance_max'].round().astype(int).astype(str) + '%'
            
            combined_cards['deck_chance_string'] = combined_cards['deck_chance'] * 100
            combined_cards['deck_chance_string'] = combined_cards['deck_chance_string'].round().astype(float).astype(str) + '%'

            combined_cards['weighted_cards_string'] = combined_cards['weighted_cards'].round(1).astype(float).astype(str)

            combined_cards['chance_string_0'] = combined_cards['chance_min_0'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_0'].round().astype(int).astype(str) + '%'

            combined_cards['chance_string_1'] = combined_cards['chance_min_1'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_1'].round().astype(int).astype(str) + '%'

            combined_cards['chance_string_2'] = combined_cards['chance_min_2'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_2'].round().astype(int).astype(str) + '%'

            combined_cards['chance_string_3'] = combined_cards['chance_min_3'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_3'].round().astype(int).astype(str) + '%'
            # set session values of probable cards
            combined_cards = combined_cards[['cardCode', 'weighted_cards', 'cost', 'spellSpeed', 'type', 'supertype', 'name', 'region', 'deck_chance', 'chance_string', 'deck_chance_string', 'weighted_cards_string', 'chance_string_0', 'chance_string_1', 'chance_string_2', 'chance_string_3']]
            session['combined_cards'] = json.loads(combined_cards.to_json(orient='records'))
            session.modified = True

            # filter out units and spells
            units = combined_cards[combined_cards['type'] == 'Unit']
            fast_spells = combined_cards[(combined_cards['type'] == 'Spell') & (combined_cards['spellSpeed'] != 'Slow')]
            slow_spells = combined_cards[(combined_cards['type'] == 'Spell') & (combined_cards['spellSpeed'] == 'Slow')]
            #set initial values for mana and spell mana
            session['mana'] = 10
            mana = session.get("mana", None)
            session['spell_mana'] = 3
            spell_mana = session.get("spell_mana", None)
            # filter probable cards by mana values
            if units.empty:
               pass
            else:
               units = units[units['cost'] <= mana]

            if fast_spells.empty:
               pass
            else:
               fast_spells = fast_spells[(fast_spells['cost'] <= mana + spell_mana)]
            
            if slow_spells.empty:
               pass
            else:
               slow_spells = slow_spells[(slow_spells['cost'] <= mana + spell_mana)]
            # Turn cards dataframes into json
            units = json.loads(units.to_json(orient='records'))
            fast_spells = json.loads(fast_spells.to_json(orient='records'))
            slow_spells = json.loads(slow_spells.to_json(orient='records'))
            return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana, units=units, fast_spells=fast_spells, slow_spells=slow_spells, deck_count=deck_count, round_n=round_n)
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana, units=units, fast_spells=fast_spells, slow_spells=slow_spells, deck_count=deck_count,round_n=round_n)

@app.route('/game_update', methods=['GET', 'POST'])
def game_update():
   # get and update mana values
   session['mana'] = request.form.get('mana')
   mana = session.get("mana", None)
   session['spell_mana'] = request.form.get('spell_mana')
   spell_mana = session.get("spell_mana", None)
   session['round_n'] = request.form.get('round_n')
   round_n = session.get("round_n", None)
   deck_count = session.get("deck_count", None)

   filtered_champions = session.get("filtered_champions", None)
   combined_cards = pd.DataFrame.from_dict(pd.json_normalize(session.get("combined_cards", None)), orient='columns')
   #combined_cards.reset_index(inplace=True, drop=True)
   # recalculate probabilities
   combined_cards['draw_min'] = combined_cards.groupby(['cardCode']).apply(draw_min, 'weighted_cards', int(round_n),0).reset_index()[0]
   combined_cards['draw_max'] = combined_cards.groupby(['cardCode']).apply(draw_max, 'weighted_cards', int(round_n), 0).reset_index()[0]
   
   combined_cards['draw_min_1'] = combined_cards.groupby(['cardCode']).apply(draw_min_1, 'weighted_cards', int(round_n)).reset_index()[0]
   combined_cards['draw_max_1'] = combined_cards.groupby(['cardCode']).apply(draw_max_1, 'weighted_cards', int(round_n)).reset_index()[0]

   combined_cards['draw_min_2'] = combined_cards.groupby(['cardCode']).apply(draw_min_2, 'weighted_cards', int(round_n)).reset_index()[0]
   combined_cards['draw_max_2'] = combined_cards.groupby(['cardCode']).apply(draw_max_2, 'weighted_cards', int(round_n)).reset_index()[0]

   combined_cards['draw_min_3'] = 1- ((1-combined_cards['draw_min']) + combined_cards['draw_min_1']+combined_cards['draw_min_2'])
   combined_cards['draw_max_3'] = 1- ((1-combined_cards['draw_max']) + combined_cards['draw_max_1']+combined_cards['draw_max_2'])

   combined_cards['chance_min'] = combined_cards['deck_chance'] * combined_cards['draw_min'] * 100
   combined_cards['chance_max'] = combined_cards['deck_chance'] * combined_cards['draw_max'] * 100

   combined_cards['chance_min_1'] = combined_cards['deck_chance'] * (combined_cards['draw_min_1']) * 100
   combined_cards['chance_max_1'] = combined_cards['deck_chance'] * (combined_cards['draw_max_1']) * 100

   combined_cards['chance_min_2'] = combined_cards['deck_chance'] * (combined_cards['draw_min_2']) * 100
   combined_cards['chance_max_2'] = combined_cards['deck_chance'] * (combined_cards['draw_max_2']) * 100

   combined_cards['chance_min_3'] = combined_cards['deck_chance'] * (combined_cards['draw_min_3']) * 100
   combined_cards['chance_max_3'] = combined_cards['deck_chance'] * (combined_cards['draw_max_3']) * 100

   combined_cards['chance_min_0'] = combined_cards['deck_chance'] * (1 - combined_cards['draw_max']) * 100
   combined_cards['chance_max_0'] = combined_cards['deck_chance'] * (1 - combined_cards['draw_min']) * 100

   combined_cards['chance_string'] = combined_cards['chance_min'].round().astype(int).astype(str) + '-' + combined_cards['chance_max'].round().astype(int).astype(str) + '%'

   combined_cards['chance_string_0'] = combined_cards['chance_min_0'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_0'].round().astype(int).astype(str) + '%'

   combined_cards['chance_string_1'] = combined_cards['chance_min_1'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_1'].round().astype(int).astype(str) + '%'

   combined_cards['chance_string_2'] = combined_cards['chance_min_2'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_2'].round().astype(int).astype(str) + '%'

   combined_cards['chance_string_3'] = combined_cards['chance_min_3'].round().astype(int).astype(str) + '-' + combined_cards['chance_max_3'].round().astype(int).astype(str) + '%'

   # filter out units and spells
   units = combined_cards[combined_cards['type'] == 'Unit']
   fast_spells = combined_cards[(combined_cards['type'] == 'Spell') & (combined_cards['spellSpeed'] != 'Slow')]
   slow_spells = combined_cards[(combined_cards['type'] == 'Spell') & (combined_cards['spellSpeed'] == 'Slow')]
   # set session values of probable cards
   combined_cards = combined_cards[['cardCode', 'weighted_cards', 'cost', 'spellSpeed', 'type', 'supertype', 'name', 'region', 'deck_chance', 'chance_string', 'deck_chance_string', 'weighted_cards_string', 'chance_string_0', 'chance_string_1', 'chance_string_2', 'chance_string_3']]
   session['combined_cards'] = json.loads(combined_cards.to_json(orient='records'))
   session.modified = True

   # filter probable cards by mana values
   if units.empty:
      pass
   else:
      units = units[units['cost'] <= int(mana)]

   if fast_spells.empty:
      pass
   else:
      fast_spells = fast_spells[(fast_spells['cost'] <= int(mana) + int(spell_mana))]
   
   if slow_spells.empty:
      pass
   else:
      slow_spells = slow_spells[(slow_spells['cost'] <= int(mana) + int(spell_mana))]
   # Turn cards dataframes into json
   units = json.loads(units.to_json(orient='records'))
   fast_spells = json.loads(fast_spells.to_json(orient='records'))
   slow_spells = json.loads(slow_spells.to_json(orient='records'))
   return render_template("public/game.html", regions=regions, filtered_champions=filtered_champions, mana=mana, spell_mana=spell_mana, units=units, fast_spells=fast_spells, slow_spells=slow_spells, deck_count=deck_count, round_n=round_n)

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

@app.route('/sitemap.xml')
def site_map():
  return render_template('/sitemap.xml', base_url="https://elusive.gg")