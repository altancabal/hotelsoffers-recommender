from flask import Flask
from flask_cors import CORS
import os
from notion_client import Client
from pprint import pprint

import pandas as pd

#notion = Client(auth=os.environ["NOTION_TOKEN"])

app = Flask(__name__)
CORS(app)

#Google Sheets
SHEET_ID = '1NjsxyTPkdM-5NmkLxjk_mRNdIi7S_qb4h1J525F-YeE'
SHEET_NAME = 'Sheet1'

notion = Client(auth=os.environ["NOTION_TOKEN"])
#The Notion database "Vuelos" - https://www.notion.so/exploradordeviajes/76dea96154c14c2e9ee606de094f0c9c?v=3af9e9b1a8724910a86bda1ac8e90b36
vuelos_database_id = "76dea961-54c1-4c2e-9ee6-06de094f0c9c"


###################################################
## 1. FETCH PROMO INFORMATION FROM GOOGLE SHEETS ##
###################################################

def fetchRawPromosInformationFromGSheets():
  url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
  return pd.read_csv(url, names=["verifiedDate", "promo_id", "kayak_url", "price", "primerProveedor", "maletasDeMano", "maletasFacturadas", "idaHoras", "idaAerolineas", "idaEscalas", "idaLugaresEscalas", "idaDuracion", "idaOrigenDestino", "vueltaHoras", "vueltaAerolineas", "vueltaEscalas", "vueltaLugaresEscalas", "vueltaDuracion", "vueltaOrigenDestino"])


def getUuidRowNumbers(pd, column_name):
  uuid_pattern = r'\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b'
  # Create a boolean mask that indicates which rows contain a UUID in the 'verifiedDate' column
  mask = pd[column_name].str.contains(uuid_pattern)
  # Get the row numbers for the rows that match the mask
  row_numbers = pd[mask].index
  return row_numbers 


def formatPrice(price_str):
  return int(price_str.replace('$', '').replace(' ', '').replace(',', ''))


def formatCommaSeparatedValuesToArray(string):
  array = [s.strip() for s in string.split(',')]
  filtered_list = [x for x in array if x != 'nan'] #Remove all None values
  return filtered_list


def createFlightDataFromPandaRow(row):
  row = row.copy()
  
  row['price'] = formatPrice(row['price'])
  row['maletasDeMano'] = row['maletasDeMano'].astype(int)
  row['maletasFacturadas'] = pd.to_numeric(row['maletasFacturadas'], downcast='integer')
  row['idaAerolineas'] = row['idaAerolineas'].strip()
  row['vueltaAerolineas'] = row['vueltaAerolineas'].strip()
  row['idaLugaresEscalas'] = str(row['idaLugaresEscalas']).strip()
  row['vueltaLugaresEscalas'] = str(row['vueltaLugaresEscalas']).strip()
  row['idaDuracion'] = row['idaDuracion'].strip()
  row['vueltaDuracion'] = row['vueltaDuracion'].strip()
  row['idaEscalas'] = row['idaEscalas'].strip()
  row['vueltaEscalas'] = row['vueltaEscalas'].strip()
  
  return row.to_dict()


def getSimplePromoDict(raw_pd):
  flights = []
  for i in range(len(raw_pd)):
    flight = createFlightDataFromPandaRow(raw_pd.iloc[i])
    flights.append(flight)

  return flights
  

def getPromoDict(raw_pd, first_row, final_row):
  promo = {}
  promo["promo_id"] = raw_pd.iloc[first_row]['verifiedDate'] #The first column is verifiedDate
  promo["kayak_url"] = raw_pd.iloc[first_row + 1]['verifiedDate']

  flights = []
  for i in range(first_row + 2, min(final_row + 1, len(raw_pd))):
    flight = createFlightDataFromPandaRow(raw_pd.iloc[i])
    flights.append(flight)

  return {
    "promo_id": promo["promo_id"],
    "kayak_url": promo["kayak_url"],
    "flights": flights
  }


def formatBestPromosDataFromPDAndUuidRowNumbers(raw_pd, uuid_row_numbers):
  promos = []
  for i in range(len(uuid_row_numbers)):
    first_value = uuid_row_numbers[i]
    last_value = len(raw_pd)
    if (i + 1) < len(uuid_row_numbers):
      last_value = uuid_row_numbers[i+1]-1
    promo = getPromoDict(raw_pd, first_value, last_value)
    promos.append(promo)
  return promos
  

def fetchPromosInformationFromGSheets():
  raw_data_pd = fetchRawPromosInformationFromGSheets()
  promos = getSimplePromoDict(raw_data_pd)
  #uuid_row_numbers = getUuidRowNumbers(raw_data_pd, 'verifiedDate')
  #promos = formatBestPromosDataFromPDAndUuidRowNumbers(raw_data_pd, uuid_row_numbers)
  return promos



###########################################
## 2. UPDDATE FLIGHTS IN VUELOS DATABASE ##
###########################################

def buildUpdateProperties(promo):
  return {
      "verifiedDate": {
            "date": {
                "start": promo["verifiedDate"]
            }
        },
        "idaAerolineas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaAerolineas"]
                    }
                }
            ]
        },
        "idaDuracion": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaDuracion"]
                    }
                }
            ]
        },
        "idaEscalas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaEscalas"]
                    }
                }
            ]
        },
        "idaHoras": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaHoras"]
                    }
                }
            ]
        },
        "idaLugaresEscalas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaLugaresEscalas"]
                    }
                }
            ]
        },
        "idaOrigenDestino": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["idaOrigenDestino"]
                    }
                }
            ]
        },
        "vueltaAerolineas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaAerolineas"]
                    }
                }
            ]
        },
        "vueltaDuracion": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaDuracion"]
                    }
                }
            ]
        },
        "vueltaEscalas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaEscalas"]
                    }
                }
            ]
        },
        "vueltaHoras": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaHoras"]
                    }
                }
            ]
        },
        "vueltaLugaresEscalas": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaLugaresEscalas"]
                    }
                }
            ]
        },
        "vueltaOrigenDestino": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["vueltaOrigenDestino"]
                    }
                }
            ]
        },
        "primerProveedor": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": promo["primerProveedor"]
                    }
                }
            ]
        },
        "maletasDeMano": {
            "type": "number",
            "number": promo["maletasDeMano"]
        },
        "maletasFacturadas": {
            "type": "number",
            "number": promo["maletasFacturadas"]
        },
        "price": {
            "type": "number",
            "number": promo["price"]
        }
    }


def getBestFlight(flights):
  best_flight = {}
  lowest_flight_price = 5000 #Setting a maximum of $5000 for a flight
  for flight in flights:
    if flight["price"] < lowest_flight_price:
      lowest_flight_price = flight["price"]
      best_flight = flight

  return best_flight
    

def updateVuelosDatabaseWithPromos(promos):
  for promo in promos:
    print("promo")
    print(promo)
    #best_flight = getBestFlight(promo["flights"])
    update_properties = buildUpdateProperties(promo)
    print("---")
    print("PATCH " + "https://api.notion.com/v1/pages/" + promo["promo_id"])
    notion.pages.update(page_id=promo["promo_id"], properties=update_properties)
    #print(update_properties)


def keepOnlyLowestPricedValueOnSameId(promos):
  # Initialize an empty dictionary
  id_dict = {}
  
  # Iterate through the list of dictionaries
  for d in promos:
    # If the id is not in the dictionary, add it as a key and the dictionary as the value
    if d["promo_id"] not in id_dict:
      id_dict[d["promo_id"]] = [d]
    # If the id is already in the dictionary, append the dictionary to the list of dictionaries
    else:
      id_dict[d["promo_id"]].append(d)
  
  # Initialize an empty list to store the dictionaries with the lowest prices
  filtered_list = []
  
  # Iterate through the dictionary
  for id_key, dict_list in id_dict.items():
    # Find the dictionary with the lowest price
    lowest_price_dict = min(dict_list, key=lambda x: x["price"])
    # Append the dictionary with the lowest price to the list
    filtered_list.append(lowest_price_dict)

  return filtered_list


@app.route('/')
def index():
  return {"message": "Use the /migrate endpoint to migrate the data from Google Sheets to Notion"}


@app.route('/migrate')
def migrate():
  promos = fetchPromosInformationFromGSheets()
  print(len(promos))
  lowestPricesPromos = keepOnlyLowestPricedValueOnSameId(promos)
  print(len(lowestPricesPromos))
  updateVuelosDatabaseWithPromos(promos)
  return {"status":200}


app.run(host='0.0.0.0', port=81)
