from bs4 import BeautifulSoup
from config import SHEET_ID, SHEET_NAME

import pandas as pd
import re
import uuid


def fetchHotelsInformationFromGSheets():
  raw_data_pd = fetchRawPromosInformationFromGSheets()
  promos = getHotelDict(raw_data_pd)
  return promos


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

  # Modify URL
  base_url = "https://www.kayak.co.cr/in?a=explorador&enc_pid=deeplinks&url="
  match = re.search('/hotels/.+', row['url'])
  if match:
      row['url'] = base_url + match.group(0)
  
  # extract dates  
  url = row['url'].strip()
  dates = re.search('/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})/', url)
  if dates:
    row['start_date'] = dates.group(1)
    row['end_date'] = dates.group(2)
  
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
    required_fields = ["name", "price", "opinion_count", "location", "top_provider", "url", "rating", "img_html"]
    
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

    return True
