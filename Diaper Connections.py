import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Diaper Connections"]
collection.drop()

# URL of the website to scrape
URL = 'https://www.thediaperbank.org/diaper-connections/'

# Send a GET request to the website
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Define blocks to scrape
blocks = [
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_1 et_pb_css_mix_blend_mode_passthrough et-last-child'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_2 et_pb_css_mix_blend_mode_passthrough'},
    {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_5 et_pb_css_mix_blend_mode_passthrough et-last-child'}
]

documents = []

for block in blocks:
    for div in soup.find_all('div', class_=block['class']):
        # Extracting text from the div
        text = div.get_text(strip=True)
        # Creating a document for MongoDB
        document = {
            'text': text
        }
        documents.append(document)

# Insert documents into MongoDB
if documents:
    result = collection.insert_many(documents)
    print(f'{len(result.inserted_ids)} documents inserted.')
else:
    print('No data found to insert.')

# Close MongoDB connection
client.close()
