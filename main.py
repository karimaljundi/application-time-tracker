from win32gui import GetWindowText, GetForegroundWindow
import time
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, timedelta

load_dotenv(find_dotenv())

uri=os.environ.get("MONGODB_URI")
client=MongoClient(uri)

db=client['main']
minutesCollection = db.minutes
secondsCollection = db.seconds
hoursCollection = db.hours

def updateSecondsCollection(string, collection):
    findUpdate=collection.find_one_and_update(
        {"application": string},
        {"$inc": {"seconds": 1}}
    )
    print(findUpdate)
    if(findUpdate==None):
        add_document = {
            "date": datetime.today().strftime('%Y-%m-%d'),
            "application": string,
            "time": datetime.today().strftime('%H:%M:%S'),
            "seconds": 1
        }
        return collection.insert_one(add_document).inserted_id

def updateMinutesCollection(applications, collection):
    seconds_cursor = secondsCollection.find({}, {'seconds': 1, '_id': 0})
    total_seconds = [doc['seconds'] for doc in seconds_cursor]

    # Attempt to find and update the document, appending applications if found
    findUpdate = collection.find_one_and_update(
        {"totalSeconds": total_seconds},
        {"$set": {"date": datetime.today().strftime('%Y-%m-%d'), "time": datetime.today().strftime('%H:%M:%S')}, 
        "$push": {"applications": applications}},
        
    )

    print(findUpdate)

    # If no document is found, insert a new one
    if findUpdate is None:
        add_document = {
            "date": datetime.today().strftime('%Y-%m-%d'),
            "applications": applications,
            "time": datetime.today().strftime('%H:%M:%S'),
            "totalSeconds": total_seconds
        }
        return collection.insert_one(add_document).inserted_id

def second():
    currentWindow = GetWindowText(GetForegroundWindow())
    print("seconds", currentWindow)
    doc = updateSecondsCollection(currentWindow, collection=secondsCollection)
    time.sleep(1)
    return doc

def minute():
    minutesCollection = db.minutes
    applications = []
    secondsCollection = db.seconds
    for i in range(60):
        item= second()
        applications.append({item})
    updateMinutesCollection(applications, collection=minutesCollection)
    print(applications)
        
    return

def hour():
    return

def update_application_usage(collection, application_name, duration):
    # Convert timedelta to seconds
    duration_seconds = int(duration.total_seconds())
    
    collection.update_one(
        {"application": application_name},
        {
            "$inc": {"usage_time": duration_seconds},
            "$setOnInsert": {"application": application_name}
        },
        upsert=True
    )

def track_application_usage(duration=timedelta(minutes=1)):
    start_time = datetime.now()
    end_time = start_time + duration
    
    while datetime.now() < end_time:
        current_window = GetWindowText(GetForegroundWindow())
        update_application_usage(db.application_usage, current_window, timedelta(seconds=1))
        time.sleep(1)

def main():
    while True:
        track_application_usage()

if __name__ == '__main__':
    main()