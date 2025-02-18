import requests
import certifi
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from bson import ObjectId

# Scrape data
url = 'https://portal.ct.gov/oca/miscellaneous/miscellaneous/resources/resource-list'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize data list
data = []

# Function to parse items and descriptions from the siblings
def parse_items_and_descriptions(start_ul):
    items = []
    descriptions = []
    ul = start_ul

    while ul:
        for li in ul.find_all('li'):
            link = li.find('a')
            link_text = link.get_text(strip=True) if link else ''
            link_href = link['href'] if link else ''
            items.append({
                'text': link_text,
                'href': link_href
            })
        
        # Find the next description <p> tag
        next_p = ul.find_next_sibling('p', style='text-align: justify;')
        if next_p:
            descriptions.append(next_p.get_text(strip=True))
        
        # Move to the next <ul> if it exists
        ul = next_p.find_next_sibling('ul', style='list-style-type: disc;') if next_p else None

    return items, descriptions

# Extract data
heading = None
for tag in soup.find_all(['p', 'ul']):
    if tag.name == 'p' and 'margin-bottom: 0in;' in tag.get('style', ''):
        if heading:
            # Save previous heading's data before starting a new one
            data.append({
                'title': heading['title'],
                'items': heading['items'],
                'descriptions': heading['descriptions']
            })

        # Start a new heading
        heading = {
            'title': tag.get_text(strip=True),
            'items': [],
            'descriptions': []
        }

        # Parse items and descriptions starting from the next sibling <ul>
        next_ul = tag.find_next_sibling('ul', style='list-style-type: disc;')
        if next_ul:
            heading['items'], heading['descriptions'] = parse_items_and_descriptions(next_ul)
    
# Append the last heading
if heading:
    data.append({
        'title': heading['title'],
        'items': heading['items'],
        'descriptions': heading['descriptions']
    })

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Connecticut Resource Directory"]
collection.drop()

# Insert data with handling duplicates based on a unique field (e.g., title)

for item in data:
    collection.update_one(
        {'title': item['title']},  # Unique field for conflict resolution
        {'$set': item},
        upsert=True
    )

print("Data insertion complete.")

client.close()
