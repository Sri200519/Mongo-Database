import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import certifi


# Connect to MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Birth to 3 Programs"]
collection.drop()

# List of URLs to scrape
URLs = [
    'https://www.birth23.org/programs/?town&program_type',
    'https://www.birth23.org/programs/page/2/?town&program_type'
]

# Define User-Agent string
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_program_info(div):
    """Extract program information from a div block."""
    title = div.find('h3').get_text(strip=True) if div.find('h3') else 'No Title'
    category = div.find('div', class_='program-block-categories').get_text(strip=True) if div.find('div', class_='program-block-categories') else 'No Category'
    
    # Extract contact email
    contact_div = div.find('div', class_='program-block-contact')
    contact_email = 'No Contact Email'
    if contact_div:
        email_link = contact_div.find('a')
        if email_link and 'href' in email_link.attrs:
            contact_email = email_link.attrs['href'].replace('mailto:', '')
        else:
            contact_email = contact_div.get_text(strip=True)
    
    # Extract phone number
    phone_number = div.find('div', class_='program-block-phone').get_text(strip=True) if div.find('div', class_='program-block-phone') else 'No Phone Number'
    
    return {
        'title': title,
        'category': category,
        'contact_email': contact_email,
        'phone_number': phone_number
    }

# Iterate over each URL
for URL in URLs:
    print(f'Scraping {URL}')
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Print the page title for debugging
            print(f'Page Title: {soup.title.string}')

            # Define block to scrape
            blocks = soup.find_all('div', class_='loop-program program-block program-post')

            # Check if any blocks are found
            if not blocks:
                print(f'No blocks found on {URL}.')
                continue

            # Extract data and prepare for MongoDB
            documents = []
            for block in blocks:
                program_info = extract_program_info(block)
                documents.append(program_info)

            # Insert documents into MongoDB
            if documents:
                result = collection.insert_many(documents)
                print(f'{len(result.inserted_ids)} documents inserted from {URL}.')
            else:
                print(f'No data found to insert from {URL}.')
        else:
            print(f'Failed to retrieve {URL} with status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred while scraping {URL}: {e}')

# Close MongoDB connection
client.close()