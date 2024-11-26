import logging
from datetime import datetime
import json

from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()



# Define a Pydantic model for the parsed URL data
class ParsedURLData(BaseModel):
    main_domain: str
    year: Optional[int]  # Optional because the year parameter might not exist

def parse_url(url: str) -> ParsedURLData:
    # Parse the URL
    parsed = urlparse(url)
    
    # Construct the main domain and remove any trailing slash
    main_domain = f"{parsed.scheme}://{parsed.netloc}".rstrip('/')
    
    # Extract the query parameters
    query_params = parse_qs(parsed.query)
    
    # Get the year parameter as an integer, if available
    year = query_params.get('year', [None])[0]
    year = int(year) if year and year.isdigit() else None
    
    # Validate and return using the Pydantic model
    return ParsedURLData(main_domain=main_domain, year=year)

# Helper function to parse date strings into datetime objects
def parse_date(date_str):
    return datetime.strptime(date_str, "%d/%B/%Y")

# use database to store articles
def save_to_file(data, filename="press_releases.json"):
    """Save extracted data to a file."""
    import json
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        logger.info(f"Data saved to {filename}.")
    except Exception as e:
        logger.error(f"Failed to save data to file: {e}")

# read db for the latest data
def read_db(db_link):
    """Load the data from the JSON file."""
    try:
        with open(db_link, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to update db with only new entries from scarpped data
def update_db(db:list[dict], scrapped_data:list[dict]):
    
    # Find the latest date in db
    if len(db):
        latest_date_db = parse_date(db[0]['date'])

        # Filter scrapped data to include only newer dates than the latest in db
        new_entries = [entry for entry in scrapped_data if parse_date(entry.get('date')) > latest_date_db]
    
        # Prepend new entries to l1 (as l1 is sorted by latest date first)
        db = new_entries + db
        return db, new_entries
    db = scrapped_data
    new_entries = scrapped_data
    return db, new_entries

# Function to find new entries
def find_new_entries(db:list[dict], scrapped_data:list[dict]):
    
    # Find the latest date in db
    if len(db):
        latest_date_db = parse_date(db[0]['date'])

        # Filter scrapped data to include only newer dates than the latest in db
        new_entries = [entry for entry in scrapped_data if parse_date(entry.get('date')) > latest_date_db]
        return new_entries
    return scrapped_data

if __name__ == "__main__":
    url = "https://www.proofpoint.com/us/newsroom/press-releases?year=2024"
    url_meta_data = parse_url(url)
    print(f"main domain: {url_meta_data.main_domain}\nyear: {url_meta_data.year}")
    