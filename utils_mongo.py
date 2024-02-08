from pymongo import MongoClient
from datetime import datetime
import pytz

## Databas
class MongoUtils:

    def connect_to_mongodb(db_name, client_name):
        client = MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        collection = db[client_name]
        return collection

    def save_new_db(event, collection):
        collection.insert_one(event)
        print("Added event to DB")

    def update_event_db(collection, event_id, updated_event):
        collection.update_one(
        {"id": event_id},
        {"$set": updated_event}
    )
        print("Updated event in DB")

    def delete_event_db(collection, event_id):
        collection.delete_one({"id": event_id})
        print("Deleted event from DB")

    def get_event_db(collection, event_id):
        return collection.find_one({"id": event_id})

    def list_events_db(collection, summary=None, start_date=None, end_date=None, location=None):
        query = {}
        if summary:
            query['summary'] = summary
        if start_date:
            query['start.dateTime'] = {'$gte': start_date}
        if end_date:
            query['end.dateTime'] = {'$lte': end_date}
        if location:
            query['location'] = location
        
        events = collection.find(query)
        return list(events)
    
