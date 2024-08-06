import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["State Education Resource Center"]
collection.drop()

# URL of the webpage to scrape
url = 'https://ctserc.org/services'

# Make an HTTP GET request to the webpage
response = requests.get(url)

# Parse the HTML content of the webpage
soup = BeautifulSoup(response.content, 'html.parser')

# Find the div with the id 'serc-services'
services_div = soup.find('div', id='serc-services')

# Extract text from the div
services_text = services_div.get_text(strip=True) if services_div else 'Div with id "serc-services" not found.'

# Prepare the document to insert into MongoDB
document = {
    'source_url': url,
    'content': services_text
}

# Insert the document into MongoDB
result = collection.insert_one(document)

# Print the inserted document ID
print(f'Document inserted with ID: {result.inserted_id}')
client.close()
