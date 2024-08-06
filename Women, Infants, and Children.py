import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi

# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Women, Infants, and Children"]
collection.drop()


# Fetch the webpage content
url = 'https://portal.ct.gov/dph/wic/wic'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract data
data = []

# Define the styles to target
target_styles = [
    'margin: 0in 0in 0pt;',
    'text-align: left;'
]

# Find and extract <p> and <div> tags with the specified styles
for style in target_styles:
    for tag in soup.find_all(['p', 'div'], style=style):
        text_content = tag.get_text(strip=True)
        data.append({
            'tag': tag.name,
            'style': style,
            'content': text_content
        })
# Insert data into MongoDB
if data:
    collection.insert_many(data)
    print("Data scraped and stored in MongoDB successfully")


client.close()
