from datetime import datetime

import json
import openai

def getTop5RecommendedHotels(hotels):
    if not hotels or 'start_date' not in hotels[0] or 'end_date' not in hotels[0]:
      return {"status": 400, "error": "Failed to fetch or process hotels"}

    start_date_of_first_hotel = hotels[0]['start_date']
    end_date_of_first_hotel = hotels[0]['end_date']

    hotel_list_text = utils.createHotelString(hotels)
    top5Hotels = hotel_recommender.getTopRecommendedHotel(hotel_list_text, start_date_of_first_hotel, end_date_of_first_hotel)


def getTopRecommendedHotelFromGPT(hotels_str, start_date, end_date):
  today_date = datetime.today().strftime('%Y-%m-%d')
  completion = openai.ChatCompletion.create(
    model="gpt-4-0613",
    temperature=0,
    messages=[
      {"role": "system", "content": "From the following list of hotels, return a sorted array with the IDs of the top 5 hotels that you believe (based on what you already know from those hotels and the list I am sharing here) are the preffered by Costa Ricans to stay between the dates " + start_date + " and " + end_date + ". Today is " + today_date + ". The format must be [id1,id2,id3,id4,id5]" + hotels_str}
    ]
  )
  
  content = completion.choices[0].message['content']
  uuid_list = json.loads(content)

  return uuid_list