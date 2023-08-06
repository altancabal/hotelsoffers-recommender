from flask import Flask, render_template, Response
from flask_cors import CORS
from replit import db
from bs4 import BeautifulSoup

import pandas as pd
import uuid
import openai
import os
import json

app = Flask(__name__)
CORS(app)

#Google Sheets
SHEET_ID = '1attk70G_v7pYUF6pwmDh7NK1hPRXNYEkBHo6UvklZuQ'
SHEET_NAME = 'playasguanacaste'

#OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

###################################################
## 1. FETCH PROMO INFORMATION FROM GOOGLE SHEETS ##
###################################################

def fetchRawPromosInformationFromGSheets():
  url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
  return pd.read_csv(url, names=["name", "price", "opinion_count", "location", "top_provider", "url", "rating", "img_html"])


def formatPrice(price_str):
  return int(price_str.replace('$', '').replace(' ', '').replace(',', ''))


def createHotelDataFromPandaRow(row):
  row = row.copy()

  row['uuid'] = str(uuid.uuid4())
  row['price'] = formatPrice(row['price'])
  row['name'] = row['name'].strip()
  row['opinion_count'] = row['opinion_count'].strip()
  row['location'] = row['location'].strip()
  row['top_provider'] = row['top_provider'].strip()
  row['url'] = row['url'].strip()
  row['rating'] = row['rating'].strip()

  img_html = row.get('img_html', '')
  if isinstance(img_html, str):
      soup = BeautifulSoup(img_html, 'html.parser')
      img_tag = soup.find('img')
      if img_tag:
          row['img_url'] = img_tag['src']
          
          # Extract the "alt" attribute and assign it to 'name'
          #The content of 'alt' has better quality than name
          alt_text = img_tag.get('alt', '').strip()
          if alt_text:
              row['name'] = alt_text

  # Delete the 'image_url' key
  if 'img_html' in row:
      del row['img_html']
  
  return row.to_dict()


def getHotelDict(raw_pd):
  hotels = []
  for i in range(len(raw_pd)):
    hotel = createHotelDataFromPandaRow(raw_pd.iloc[i])
    hotels.append(hotel)

  return hotels


def fetchHotelsInformationFromGSheets():
  raw_data_pd = fetchRawPromosInformationFromGSheets()
  promos = getHotelDict(raw_data_pd)
  return promos


def getTopRecommendedHotel(hotels_data):
  completion = openai.ChatCompletion.create(
    model="gpt-4-0613",
    temperature=0,
    messages=[
      {"role": "system", "content": "From the following lis of hotels, return a sorted array with the IDs of the top 5 hotels that you believe (based on what you already know from those hotels and the list I am sharing here) are the preffered by Costa Ricans to stay between the dates 2023-08-11 and 2023-08-13. Today is 2023-08-06. The format must be [id1,id2,id3,id4,id5]" + hotels_data}
    ]
  )
  
  content = completion.choices[0].message['content']
  uuid_list = json.loads(content)

  return uuid_list


def createHotelString(hotels):
    columns = ["uuid", "name", "price", "opinion_count", "location", "top_provider", "url", "rating"]
    rows = [columns]  # Start with the column names

    for hotel in hotels:
        row = [str(hotel[column]) for column in columns]
        rows.append(row)

    return '\n'.join(';'.join(row) for row in rows)


def serialize(obj):
    if hasattr(obj, 'items'):
        return dict(obj)  # Convert objects with an 'items' method to a regular dict
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-top-hotel')
def getTopHotel():
  top_hotel = db["tophotel"]
  response = Response(json.dumps(top_hotel, default=serialize), content_type='application/json')
  return response


@app.route('/update')
def update():
  hotels = fetchHotelsInformationFromGSheets()
  #print("HOTELS")
  #print(hotels)
  hotel_list_text = createHotelString(hotels)
  top5Hotels = getTopRecommendedHotel(hotel_list_text)
  #print("TOP5HOTELS")
  #print(top5Hotels)
  
  top5HotelDetails = []
  for currUuid in top5Hotels:
      matching_hotel = next((hotel for hotel in hotels if hotel['uuid'] == currUuid), None)
      if matching_hotel:
          top5HotelDetails.append(matching_hotel)

  #TODO add the current date
  print("TOP5HOTELSDETAILS")
  print(top5HotelDetails)
  
  db["tophotel"] = top5HotelDetails[0]
  
  return {"status":200}



app.run(host='0.0.0.0', port=81)
