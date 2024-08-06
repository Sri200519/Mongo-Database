import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Family Support and Services"]
collection.drop()

# Fetch the webpage content
url = "https://portal.ct.gov/dds/supports-and-services/family-support-and-services?language=en_US"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Find all divs with the specified class
for div in soup.find_all('div', class_='cg-c-lead-story__body col'):
    block_content = div.get_text(strip=True, separator=' ')
    list_items = [li.get_text(strip=True) for li in div.find_all('li')]
    
    # Combine the block content with list items
    combined_content = {
        'block_content': block_content,
        'list_items': list_items
    }
    data.append(combined_content)

# Insert data into MongoDB
if data:
    collection.insert_many(data)
    print("Data scraped and stored in MongoDB successfully")

client.close()

