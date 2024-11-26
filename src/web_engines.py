import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pydantic import BaseModel
from typing import List

try:
    from src.utils import parse_url
except:
    from utils import parse_url

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Define Pydantic model for press release data
class PressRelease(BaseModel):
    title: str
    link: str
    date: str

# Define the scraper class
class PressReleaseScraper:
    def __init__(self, driver=None):
        """Initialize the scraper with a Selenium WebDriver."""
        self.driver = driver or self.setup_driver()
        self.__main_domain = None
        self.__year = None
    
    def setup_driver(self):
        """Set up the Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        try:
            driver = webdriver.Chrome(options=options)
            logger.info("Driver initialized successfully.")
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def fetch_press_releases(self, 
                             url: str, 
                             max_retries: int = 3) -> List[webdriver.remote.webelement.WebElement]:
        """Fetch press release elements from the specified URL."""
        # parse url
        url_meta_data = parse_url(url)
        self.__main_domain = url_meta_data.main_domain
        self.__year = url_meta_data.year

        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                logger.info("Navigated to the URL.")
                
                wait = WebDriverWait(self.driver, 20)
                press_release_elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.press-releases-v4__hit a"))
                )
                logger.info(f"Found {len(press_release_elements)} press releases.")
                return press_release_elements
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        logger.error("Failed to fetch press releases after retries.")
        return []

    def scrape_data(self, 
                    press_release_elements: List[webdriver.remote.webelement.WebElement]) -> List[PressRelease]:
        """Extract data from press release elements."""
        press_release_data = []
        for press_release in press_release_elements:
            try:
                title = press_release.find_element(By.TAG_NAME, "h3").text.strip()
                link = self.__main_domain + press_release.get_dom_attribute("href")
                
                date_div = press_release.find_element(By.CSS_SELECTOR, "div.press-releases-v4__hit-date")
                day = date_div.find_element(By.CLASS_NAME, "press-releases-v4__hit-date-day").text.strip()
                month = date_div.find_element(By.CLASS_NAME, "press-releases-v4__hit-date-month").text.strip()
                if self.__year is not None:
                    date = f"{day}/{month}/{self.__year}"
                else:
                    date = f"{day}/{month}"

                if title and link and date:
                    press_release_data.append(PressRelease(title=title, link=link, date=date))
                else:
                    logger.warning("Incomplete data found, skipping entry.")
            except Exception as e:
                logger.warning(f"Error extracting data: {e}")
        return press_release_data

    def close_driver(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Driver closed successfully.")

if __name__ == "__main__":
    url = "https://www.proofpoint.com/us/newsroom/press-releases?year=2024"
    scraper = PressReleaseScraper()
    
    try:
        elements = scraper.fetch_press_releases(url)
        data = scraper.scrape_data(elements)
        for item in data:
            print(item.model_dump())
    finally:
        scraper.close_driver()


    


