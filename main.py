#Third party imports
from config import app
from flask import render_template, Response

#Local imports
import hotel_fetcher
import hotel_price_storer
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
  if hotel_price_storer.already_stored_today():
      return {"status": 208, "message": "Hotel already stored today. Skipping update."}
  
  #Fetch full cleaned list of hotels
  full_list_hotels = hotel_fetcher.fetchHotelsInformationFromGSheets()
  hotels_last_two_weeks = hotel_price_storer.get_hotels_from_last_two_weeks()
  hotels = [hotel for hotel in full_list_hotels if hotel["name"] not in hotels_last_two_weeks]

  # Sort the hotels list by price in ascending order and keep the first 100
  hotels = sorted(hotels, key=lambda x: x['price'])[:100]
  
  print("Size of full_list_hotels:", len(full_list_hotels))
  print("Size of hotels_last_two_weeks:", len(hotels_last_two_weeks))
  print("Size of filtered hotels:", len(hotels))
    
  #Get the top 5 hotels
  top5HotelIDs = hotel_recommender.getTop5RecommendedHotels(hotels)
  
  #Map the top hotel IDs with their details
  top5HotelDetails = [next(hotel for hotel in hotels if hotel['uuid'] == uuid) for uuid in top5HotelIDs]

  if top5HotelDetails:
    # Check if a hotel has been stored today
    top_hotel = top5HotelDetails[0]
    print("THE TOP HOTEL IS")
    print(top_hotel)
    utils.save_to_db(TOP_HOTEL_KEY, top_hotel)
    hotel_price_storer.store_hotel(top_hotel)

  return {"status": 200, "message": "Hotel updated successfully."}



app.run(host='0.0.0.0', port=81)
