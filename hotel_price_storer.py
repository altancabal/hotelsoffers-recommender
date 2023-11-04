from datetime import datetime, timedelta
from notion_client import Client

import os
import re

notion = Client(auth=os.environ["NOTION_TOKEN"])
#The Notion database "Hoteles" - https://www.notion.so/exploradordeviajes/8b40aea49c8749afbc81f51582bf5850?v=1bf01c9b3031469889fb816a964f26e8
hoteles_database_id = "8b40aea49c8749afbc81f51582bf5850"


def already_stored_today():
    today_date = datetime.now().strftime('%Y-%m-%d')
    # Query the database with a filter
    response = notion.databases.query(
        database_id=hoteles_database_id,
        filter={
            "property": "Promo del Dia",
            "date": {
                "equals": today_date
            }
        }
    )
    # Check if any results were returned
    return bool(response["results"])


def store_hotel(hotel):
  # Extracting numeric value from opinion_count
  opinion_text = hotel["opinion_count"]
  match = re.search(r'(\d+(?:\.\d+)?)', opinion_text)
  opinion_number = int(match.group(1).replace('.', '')) if match else 0

  #Formatting the rating
  str_rating = hotel["rating"].replace(',', '.')
  rating = float(str_rating)

  #Formatting the start and end dates
  start_date_obj = datetime.strptime(hotel["start_date"], '%Y-%m-%d')
  formatted_start_date = start_date_obj.strftime('%Y-%m-%d')
  end_date_obj = datetime.strptime(hotel["end_date"], '%Y-%m-%d')
  formatted_end_date = end_date_obj.strftime('%Y-%m-%d')
  
  notion.pages.create(
      parent={"database_id": hoteles_database_id},
      properties={
          "Name": {"title": [{"text": {"content": hotel["name"]}}]},
          "Price": {"number": hotel["price"]},
          "Opinions": {"number": opinion_number},
          "Location": {"rich_text": [{"text": {"content": "Desconocido"}}]},
          "Top provider": {"rich_text": [{"text": {"content": hotel["top_provider"]}}]},
          "Promo URL": {"url": hotel["url"]},
          "Rating": {"number": rating},
          "Image URL": {"url": hotel["img_url"]},
          "Start Date": {"date": {"start": formatted_start_date}},
          "End Date": {"date": {"start": formatted_end_date}},
          "Promo del Dia": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
      }
  )


def get_hotels_from_last_two_weeks():
    two_weeks_ago_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Query the database with a filter
    response = notion.databases.query(
        database_id=hoteles_database_id,
        filter={
            "property": "Promo del Dia",
            "date": {
                "after": two_weeks_ago_date
            }
        }
    )
    
    # Extract hotel names from results
    hotel_names = [entry["properties"]["Name"]["title"][0]["text"]["content"] for entry in response["results"]]
    
    return hotel_names