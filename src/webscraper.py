import logging

from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from typing import List, Optional

class ArticleDetails(BaseModel):
    title: Optional[str]
    date: Optional[str]
    image_url: Optional[str]
    content: Optional[str]


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def fetch_html(self):
        """Fetch the HTML content from the URL."""
        response = requests.get(self.url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'html.parser')
        else:
            raise Exception(f"Failed to fetch HTML content. Status code: {response.status_code}")

    def get_article_details(self)->ArticleDetails:
        """Extracts and returns details from the article."""
        if not self.soup:
            raise Exception("HTML content not fetched. Call fetch_html() first.")

        article = self.soup.find('article', class_='node--type--news')
        if not article:
            return None

        # Extract title
        title = article.find('h3', class_='news-main-content__title')
        title_text = title.find('span').get_text(strip=True) if title else None

        # Extract date
        date = article.find('time')
        date_text = date.get_text(strip=True) if date else None

        # Extract image URL
        image = article.find('div', class_='news-main-content__image').find('img')
        image_url = image['src'] if image else None

        # Extract content paragraphs
        content_div = article.find('div', class_='node-full__body')
        content_paragraphs = [p.get_text(strip=True) for p in content_div.find_all('p')] if content_div else []
        if len(content_paragraphs):
            narrative_text = "\n".join(content_paragraphs)
        else:
            narrative_text = ""

        return ArticleDetails(
            title=title_text,
            date=date_text,
            image_url=image_url,
            content=narrative_text)

    def scrape(self):
        """Fetches HTML content and scrapes article details."""
        self.fetch_html()
        return self.get_article_details()


if __name__ == "__main__":
    url ="https://www.proofpoint.com/us/newsroom/press-releases/american-retailers-expose-consumers-holiday-shopping-email-fraud"
    scraper = WebScraper(url)
    
    try:
        article_details = scraper.scrape()
        if article_details:
            logger.info("Article Details:")
            logger.info(f"Title: {article_details.title}")
            logger.info(f"Date: {article_details.date}")
            logger.info(f"Image URL: {article_details.image_url}")
            logger.info(f"Content: {article_details.content}")
        else:
            logger.info("No article details found.")
    except Exception as e:
        print(f"Error: {e}")
