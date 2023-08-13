import json

def createHotelString(hotels):
    columns = ["uuid", "name", "price", "opinion_count", "location", "rating"]
    rows = [columns]  # Start with the column names

    for hotel in hotels:
        row = [str(hotel[column]) for column in columns]
        rows.append(row)
  
    return '\n'.join(';'.join(row) for row in rows)


def serialize(obj):
    if hasattr(obj, 'items'):
        return dict(obj)  # Convert objects with an 'items' method to a regular dict
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


def to_json(data):
    return json.dumps(data, default=serialize)


#DB methods
def fetch_from_db(key):
    from replit import db  # Move this import here to avoid circular imports
    return db[key]

def save_to_db(key, value):
    from replit import db  # Move this import here to avoid circular imports
    db[key] = value;