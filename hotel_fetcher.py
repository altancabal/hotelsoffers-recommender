from bs4 import BeautifulSoup
from config import SHEET_ID, SHEET_NAME, PRICE_LIMIT, MIN_OPINIONS_LIMIT
from datetime import datetime

import pandas as pd
import re
import uuid


def fetchHotelsInformationFromGSheets():
  raw_data_pd = fetchRawPromosInformationFromGSheets()
  promos = getHotelDict(raw_data_pd)
  return promos


def fetchRawPromosInformationFromGSheets():
  url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
  return pd.read_csv(url, names=["name", "price", "opinion_count", "top_provider", "url", "rating", "img_url", "fetched_date"])


def formatPrice(price_str):
  return int(price_str.replace('$', '').replace(' ', '').replace(',', '').replace('.', '').replace('*', ''))

def getIntOpinionsValue(opinions_str):
  return int(opinions_str.replace(' opiniones', '').replace(' opinión', '').replace(',', '').replace('.', ''))

def extract_alt_with_regex(html_content):
    # Modified regex to account for escaped quotes and capture content within
    alt_pattern = r'alt\\s*=\\s*\\"([^\\"]+)\\"'
    match = re.search(alt_pattern, html_content)
    return match.group(1) if match else ""


def createHotelDataFromPandaRow(row):
    row = row.copy()
    row['uuid'] = str(uuid.uuid4())
    row['price'] = formatPrice(row['price'])
    row['location'] = 'Desconocido'
    
    fields_to_strip = ['name', 'opinion_count', 'top_provider', 'url', 'rating']
    for field in fields_to_strip:
      row[field] = row[field].strip()

    # Modify URL
    base_url = "https://www.kayak.co.cr/in?a=explorador&enc_pid=deeplinks&url="
    match = re.search('/hotels/.+', row['url'])
    if match:
        row['url'] = base_url + match.group(0)

    # Extract dates  
    dates = re.search('/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/', row['url'])
    if dates:
        row['start_date'] = dates.group(1)
        row['end_date'] = dates.group(2)

    return row.to_dict()


def getHotelDict(raw_pd):
    hotels = []
    seen_hotels = set()  # To keep track of hotel names that have been added

    for i in range(len(raw_pd)):
        # If row is valid, process it
        if is_valid_row(raw_pd.iloc[i]):
            hotel = createHotelDataFromPandaRow(raw_pd.iloc[i])
            hotel_name = hotel['name']

            # If the hotel name hasn't been added before, append it to the list
            if hotel_name not in seen_hotels:
                hotels.append(hotel)
                seen_hotels.add(hotel_name)  # Mark the hotel name as seen

    return hotels


def is_valid_row(row):
    # List of required fields
    required_fields = ["name", "price", "opinion_count", "top_provider", "url", "rating", "img_url", "fetched_date"]
    
    # Check if each field exists and is not empty
    for field in required_fields:
        # Check if field exists in the row
        if field not in row:
            return False
        
        # Check if the field is not empty (considering spaces, None, etc.)
        if not row[field] or str(row[field]).strip() == '':
            return False

        # Specific check for the price field
        if field == "price" and not str(row[field]).startswith('$'):
            return False
        if field == "price" and formatPrice(row[field]) > PRICE_LIMIT:
            return False

        #Specific check for opinions count
        if field == "opinion_count" and getIntOpinionsValue(row[field]) < MIN_OPINIONS_LIMIT:
            return False
      
        if field == "fetched_date" and row[field] != datetime.today().strftime('%Y-%m-%d'):
            return False

    return True
