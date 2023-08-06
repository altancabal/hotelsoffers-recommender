from flask import Flask
from flask_cors import CORS

import pandas as pd
import uuid

app = Flask(__name__)
CORS(app)

#Google Sheets
SHEET_ID = '1attk70G_v7pYUF6pwmDh7NK1hPRXNYEkBHo6UvklZuQ'
SHEET_NAME = 'playasguanacaste'


###################################################
## 1. FETCH PROMO INFORMATION FROM GOOGLE SHEETS ##
###################################################

def fetchRawPromosInformationFromGSheets():
  url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
  return pd.read_csv(url, names=["name", "price", "opinion_count", "location", "top_provider", "url", "rating"])


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
  
  return row.to_dict()


def getHotelDict(raw_pd):
  hotels = []
  for i in range(len(raw_pd)):
    hotel = createHotelDataFromPandaRow(raw_pd.iloc[i])
    hotels.append(hotel)

  return hotels


def fetchPromosInformationFromGSheets():
  raw_data_pd = fetchRawPromosInformationFromGSheets()
  promos = getHotelDict(raw_data_pd)
  return promos


@app.route('/')
def index():
  return {"message": "Use the /migrate endpoint to migrate the data from Google Sheets to Notion"}


@app.route('/migrate')
def migrate():
  promos = fetchPromosInformationFromGSheets()
  print(promos)
  return {"status":200}


app.run(host='0.0.0.0', port=81)
