import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Temporary Family Assistance"]
collection.drop()

# URL of the website to scrape
URL = 'https://portal.ct.gov/dss/archived-folder/temporary-family-assistance---tfa'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define block to scrape
block_class = 'content'

# Extract the content from the specified block
content_div = soup.find('div', class_=block_class)
if content_div:
    text = content_div.get_text(strip=True)
else:
    text = 'Content not found.'

# Create a document for MongoDB
document = {
    'text': text
}

# Insert document into MongoDB
result = collection.insert_one(document)
print(f'Document inserted with id: {result.inserted_id}')

# Close MongoDB connection
client.close()
