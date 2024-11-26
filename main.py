import logging
import re

from src.utils import read_db, find_new_entries, save_to_file
from src.web_engines import PressReleaseScraper
from src.webscraper import WebScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


def main():
    db_data = read_db(db_link="press_releases.json")
    url = "https://www.proofpoint.com/us/newsroom/press-releases?year=2024"
    try:
        scraper = PressReleaseScraper()
        elements = scraper.fetch_press_releases(url)
        scraped_data = scraper.scrape_data(elements)
        if scraped_data:
            data_json = [ent.model_dump() for ent in scraped_data]
            logger.info(f"Scraped {len(data_json)} press releases successfully.")
            new_entries_list = find_new_entries(db_data,data_json)
            logger.info(f"{len(new_entries_list)} new entry found")
            # scrap content from Press Realease links
            for data in new_entries_list:
                url = data["link"]
                web_scraper = WebScraper(url)
                article_details = web_scraper.scrape()
                data["content"] = article_details.content
            updated_data = new_entries_list + db_data
            save_to_file(updated_data)
        else:
            logger.info("No data extracted.")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()