"""
Web scraper for collecting product reviews from various e-commerce platforms.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from utils import clean_text, save_to_csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewScraper:
    """Base class for scraping product reviews."""
    
    def __init__(self, base_url: str, headers: dict = None):
        """
        Initialize the scraper.
        
        Args:
            base_url (str): Base URL of the target website
            headers (dict): HTTP headers for requests
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_reviews(self, product_urls: list, max_pages: int = 5):
        """
        Scrape reviews from multiple product URLs.
        
        Args:
            product_urls (list): List of product URLs to scrape
            max_pages (int): Maximum number of pages to scrape per product
            
        Returns:
            pd.DataFrame: DataFrame containing scraped reviews
        """
        all_reviews = []
        
        for url in product_urls:
            logger.info(f"Scraping reviews from: {url}")
            product_reviews = self._scrape_product_reviews(url, max_pages)
            all_reviews.extend(product_reviews)
            
            # Be respectful to the server
            time.sleep(2)
        
        return pd.DataFrame(all_reviews)
    
    def _scrape_product_reviews(self, product_url: str, max_pages: int):
        """
        Scrape reviews for a single product.
        
        Args:
            product_url (str): URL of the product page
            max_pages (int): Maximum number of pages to scrape
            
        Returns:
            list: List of review dictionaries
        """
        reviews = []
        
        for page in range(1, max_pages + 1):
            try:
                page_url = f"{product_url}?page={page}"
                response = self.session.get(page_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                page_reviews = self._parse_reviews_page(soup)
                
                if not page_reviews:
                    logger.info(f"No more reviews found on page {page}")
                    break
                
                reviews.extend(page_reviews)
                logger.info(f"Scraped {len(page_reviews)} reviews from page {page}")
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                continue
        
        return reviews
    
    def _parse_reviews_page(self, soup: BeautifulSoup):
        """
        Parse reviews from a single page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            list: List of review dictionaries
        """
        # This is a template method - implement specific parsing logic
        # based on the target website's HTML structure
        reviews = []
        
        # Example implementation (needs to be customized for specific sites)
        review_elements = soup.find_all('div', class_='review')
        
        for element in review_elements:
            try:
                review = {
                    'review_text': self._extract_review_text(element),
                    'rating': self._extract_rating(element),
                    'product_name': self._extract_product_name(element),
                    'review_date': self._extract_review_date(element)
                }
                reviews.append(review)
            except Exception as e:
                logger.warning(f"Error parsing review: {str(e)}")
                continue
        
        return reviews
    
    def _extract_review_text(self, element):
        """Extract review text from review element."""
        # Implement based on site structure
        text_elem = element.find('p', class_='review-text')
        return text_elem.text.strip() if text_elem else ""
    
    def _extract_rating(self, element):
        """Extract rating from review element."""
        # Implement based on site structure
        rating_elem = element.find('span', class_='rating')
        return int(rating_elem.text) if rating_elem else None
    
    def _extract_product_name(self, element):
        """Extract product name from review element."""
        # Implement based on site structure
        product_elem = element.find('h3', class_='product-name')
        return product_elem.text.strip() if product_elem else ""
    
    def _extract_review_date(self, element):
        """Extract review date from review element."""
        # Implement based on site structure
        date_elem = element.find('span', class_='review-date')
        return date_elem.text.strip() if date_elem else ""


def main():
    """Main function to run the scraper."""
    # Example usage
    scraper = ReviewScraper("https://example-ecommerce.com")
    
    # List of product URLs to scrape
    product_urls = [
        "https://example-ecommerce.com/product/123",
        "https://example-ecommerce.com/product/456"
    ]
    
    # Scrape reviews
    reviews_df = scraper.scrape_reviews(product_urls, max_pages=3)
    
    # Save to CSV
    save_to_csv(reviews_df, 'data/raw/reviews_raw.csv')
    logger.info(f"Scraped {len(reviews_df)} reviews successfully!")


if __name__ == "__main__":
    main()