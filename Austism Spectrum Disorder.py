import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Austism Spectrum Disorder"]
collection.drop()

# Fetch the webpage content
url = 'https://www.connecticutchildrens.org/specialties-conditions/developmental-behavioral-pediatrics/autism-spectrum-disorder-asd'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Find and extract all <p> and <h2> tags
for tag in soup.find_all(['p']):
    text_content = tag.get_text(strip=True)
    data.append({
        'tag': tag.name,
        'content': text_content
    })


# Insert data into MongoDB
if data:
    collection.insert_many(data)
    print("Data scraped and stored in MongoDB successfully")


client.close()
