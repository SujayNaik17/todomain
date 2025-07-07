"""
Utility functions for web scraping and data processing.
"""

import re
import pandas as pd
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and preprocess text data.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_rating_from_text(text: str) -> int:
    """
    Extract numeric rating from text using regex patterns.
    
    Args:
        text (str): Text containing rating information
        
    Returns:
        int: Extracted rating (1-5) or None if not found
    """
    # Common rating patterns
    patterns = [
        r'(\d+)\s*out\s*of\s*5',
        r'(\d+)\s*\/\s*5',
        r'(\d+)\s*stars?',
        r'rating:\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating = int(match.group(1))
            if 1 <= rating <= 5:
                return rating
    
    return None


def parse_date(date_string: str) -> str:
    """
    Parse date string into standardized format.
    
    Args:
        date_string (str): Raw date string
        
    Returns:
        str: Standardized date string (YYYY-MM-DD) or empty string
    """
    if not date_string:
        return ""
    
    # Common date patterns
    date_patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
        r'(\d{2})-(\d{2})-(\d{4})',  # MM-DD-YYYY
        r'(\w+)\s+(\d{1,2}),\s+(\d{4})',  # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_string)
        if match:
            try:
                if pattern == date_patterns[0]:  # YYYY-MM-DD
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                elif pattern in [date_patterns[1], date_patterns[2]]:  # MM/DD/YYYY or MM-DD-YYYY
                    month, day, year = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif pattern == date_patterns[3]:  # Month DD, YYYY
                    month_name, day, year = match.groups()
                    month_num = datetime.strptime(month_name, '%B').month
                    return f"{year}-{month_num:02d}-{day.zfill(2)}"
            except ValueError:
                continue
    
    return ""


def validate_review_data(review: Dict[str, Any]) -> bool:
    """
    Validate that a review contains required fields.
    
    Args:
        review (dict): Review dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['review_text', 'rating']
    
    for field in required_fields:
        if field not in review or not review[field]:
            return False
    
    # Validate rating range
    if not isinstance(review['rating'], int) or not (1 <= review['rating'] <= 5):
        return False
    
    # Validate review text length
    if len(review['review_text'].strip()) < 10:
        return False
    
    return True


def filter_reviews(reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out invalid or low-quality reviews.
    
    Args:
        reviews (list): List of review dictionaries
        
    Returns:
        list: Filtered list of valid reviews
    """
    valid_reviews = []
    
    for review in reviews:
        if validate_review_data(review):
            # Clean the review text
            review['review_text'] = clean_text(review['review_text'])
            valid_reviews.append(review)
        else:
            logger.warning(f"Filtered out invalid review: {review}")
    
    return valid_reviews


def save_to_csv(df: pd.DataFrame, filepath: str, add_timestamp: bool = True) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filepath (str): Output file path
        add_timestamp (bool): Whether to add timestamp to filename
    """
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = filepath.replace('.csv', f'_{timestamp}.csv')
    
    df.to_csv(filepath, index=False)
    logger.info(f"Saved {len(df)} reviews to {filepath}")


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    Remove duplicate reviews from DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with reviews
        subset (list): Columns to consider for duplicates
        
    Returns:
        pd.DataFrame: DataFrame with duplicates removed
    """
    if subset is None:
        subset = ['review_text', 'product_name']
    
    initial_count = len(df)
    df_cleaned = df.drop_duplicates(subset=subset, keep='first')
    final_count = len(df_cleaned)
    
    logger.info(f"Removed {initial_count - final_count} duplicate reviews")
    
    return df_cleaned


def get_user_agent_headers() -> Dict[str, str]:
    """
    Get common user agent headers for web scraping.
    
    Returns:
        dict: Dictionary of headers
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def create_sample_data() -> pd.DataFrame:
    """
    Create sample review data for testing.
    
    Returns:
        pd.DataFrame: Sample reviews DataFrame
    """
    sample_reviews = [
        {
            'review_id': 1,
            'review_text': 'This product is amazing! I love it so much.',
            'rating': 5,
            'product_name': 'Sample Product A',
            'review_date': '2024-01-15'
        },
        {
            'review_id': 2,
            'review_text': 'Not what I expected. Quality could be better.',
            'rating': 2,
            'product_name': 'Sample Product A',
            'review_date': '2024-01-16'
        },
        {
            'review_id': 3,
            'review_text': 'Decent product for the price. Works as expected.',
            'rating': 4,
            'product_name': 'Sample Product B',
            'review_date': '2024-01-17'
        },
        {
            'review_id': 4,
            'review_text': 'Terrible experience. Would not recommend.',
            'rating': 1,
            'product_name': 'Sample Product B',
            'review_date': '2024-01-18'
        },
        {
            'review_id': 5,
            'review_text': 'Outstanding quality and fast shipping!',
            'rating': 5,
            'product_name': 'Sample Product C',
            'review_date': '2024-01-19'
        }
    ]
    
    return pd.DataFrame(sample_reviews)