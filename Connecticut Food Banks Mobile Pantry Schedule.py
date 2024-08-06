from googleapiclient.discovery import build
from pymongo import MongoClient
from datetime import datetime
import certifi

# Configuration
API_KEY = '***'  # Replace with your Google API Key
CALENDAR_ID = 'ctfoodbank.events@gmail.com'  # Replace with your public calendar ID
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Connecticut Food Banks Mobile Pantry Schedule"]
collection.drop()

# Create the Google Calendar service object
service = build('calendar', 'v3', developerKey=API_KEY)

# Fetch events from the public calendar
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                       singleEvents=True, orderBy='startTime').execute()
events = events_result.get('items', [])

# Prepare documents for MongoDB
documents = []
for event in events:
    document = {
        'summary': event.get('summary', ''),
        'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
        'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
        'description': event.get('description', ''),
        'location': event.get('location', ''),
        'creator': event.get('creator', {}).get('email', ''),
        'id': event.get('id')
    }
    documents.append(document)

# Insert documents into MongoDB
if documents:
    result = collection.insert_many(documents)
    print(f'{len(result.inserted_ids)} documents inserted.')
else:
    print('No events found to insert.')

# Close MongoDB connection
client.close()
