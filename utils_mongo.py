from pymongo import MongoClient
from datetime import datetime
import pytz

## Database
def connect_to_mongo(db_name, client_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[client_name]
    return collection

def save_new(event, collection):
    collection.insert_one(event)
    print("Added event to DB")

def update_event(collection, iCalUID, updated_event):
    collection.update_one({"iCalUID": iCalUID}, {"$set": updated_event})
    print("Updated event in DB")

def delete_event(collection, iCalUID):
    collection.delete_one({"iCalUID": iCalUID})
    print("Deleted event from DB")

def get_event(collection, iCalUID):
    return collection.find_one({"iCalUID": iCalUID})
