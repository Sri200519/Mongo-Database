import requests
import certifi
import pdfplumber
from pymongo import MongoClient

# Step 1: Download the PDF
url = "https://portal.ct.gov/-/media/dph/cyshcn/ct-collaborative-autism-services-resource-directory.pdf"
response = requests.get(url)
with open("resource_directory.pdf", "wb") as file:
    file.write(response.content)

# Step 2: Extract Data
def extract_text_from_pdf(pdf_path):
    text_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_data.extend(page.extract_text().split('\n'))
    return text_data

pdf_text_lines = extract_text_from_pdf("resource_directory.pdf")

# Step 3: Parse Data
def parse_text(lines):
    parsed_data = []
    entry = {}
    for line in lines:
        if line.strip() == '':  # Assuming a blank line indicates a new entry
            if entry:
                parsed_data.append(entry)
                entry = {}
        else:
            if "Organization:" in line:
                if entry:  # Save the previous entry if it exists
                    parsed_data.append(entry)
                entry = {"organization": line.replace("Organization:", "").strip()}
            elif "Contact:" in line:
                entry["contact_info"] = line.replace("Contact:", "").strip()
            elif "Services:" in line:
                entry["services"] = line.replace("Services:", "").strip()
            else:
                # Handle additional lines or append to existing entry fields
                if "additional_info" in entry:
                    entry["additional_info"] += " " + line.strip()
                else:
                    entry["additional_info"] = line.strip()
    if entry:
        parsed_data.append(entry)
    return parsed_data

structured_data = parse_text(pdf_text_lines)

# Step 4: Store in MongoDB
uri = "***"
client = MongoClient(uri,tlsCAFile=certifi.where())
db = client["Trial"]
collection = db["Autism Services Resource Directory"]
collection.drop()
collection.insert_many(structured_data)

client.close()
