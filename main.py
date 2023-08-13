#Third party imports
from config import app
from flask import render_template, Response

import json
import pandas as pd

#Local imports
import config
import hotel_fetcher
import hotel_recommender
import utils

# Constants
TOP_HOTEL_KEY = "tophotel"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-top-hotel')
def getTopHotel():
  top_hotel = utils.fetch_from_db(TOP_HOTEL_KEY)
  response = Response(utils.to_json(top_hotel), content_type='application/json')
  return response


@app.route('/update')
def update():
  #Fetch full cleaned list of hotels
  hotels = hotel_fetcher.fetchHotelsInformationFromGSheets()

  #Get the top 5 hotels
  top5HotelIDs = hotel_recommender.getTop5RecommendedHotels(hotels)

  #Map the top hotel IDs with their details
  top5HotelDetails = [hotel for hotel in hotels if hotel['uuid'] in top5HotelIDs]

  if top5HotelDetails:
      utils.save_to_db(TOP_HOTEL_KEY, top5HotelDetails[0])

  return {"status": 200}



app.run(host='0.0.0.0', port=81)
