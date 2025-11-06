"""
Robust web scrapers for gathering political promise data.

This module implements scrapers with:
- requests.Session with Retry/backoff
- Descriptive User-Agent
- Default timeouts
- Safer parsing with error handling
- Only non-OAuth public scrapers

NOTE: For production use, consider:
- Using official APIs with OAuth where available
- Implementing rate limiting
- Adding caching mechanisms
- Using Redis/Celery for distributed scraping
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import feedparser

logger = logging.getLogger(__name__)

# User-Agent to identify our scraper
USER_AGENT = 'MamdaniTracker/1.0 (Educational/Research; +https://github.com/nickm538/nickm538)'

# Default timeout for all requests (connect timeout, read timeout)
DEFAULT_TIMEOUT = (10, 30)


def create_robust_session() -> requests.Session:
    """
    Create a requests.Session with retry logic and backoff.
    
    Returns:
        Configured requests.Session with retry adapter
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # Only retry safe methods
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    return session


def scrape_google_news_rss(query: str = "political promises", max_results: int = 10) -> List[Dict]:
    """
    Scrape Google News RSS feed for political news.
    
    NOTE: Google News RSS is a public feed, but for production consider:
    - Google News API (requires API key)
    - Proper attribution and terms compliance
    
    Args:
        query: Search query for news
        max_results: Maximum number of results to return
    
    Returns:
        List of dictionaries containing news data
    """
    results = []
    
    try:
        # Google News RSS URL
        encoded_query = quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Fetching Google News RSS for query: {query}")
        
        # Parse RSS feed (feedparser handles requests internally)
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning("No entries found in Google News RSS feed")
            return results
        
        for entry in feed.entries[:max_results]:
            try:
                result = {
                    'title': entry.get('title', 'No title'),
                    'description': entry.get('summary', ''),
                    'source': 'Google News',
                    'source_url': entry.get('link', ''),
                    'category': 'news',
                    'published': entry.get('published', ''),
                }
                results.append(result)
                logger.debug(f"Scraped: {result['title'][:50]}...")
                
            except Exception as e:
                logger.error(f"Error parsing RSS entry: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully scraped {len(results)} items from Google News RSS")
        
    except Exception as e:
        logger.error(f"Error scraping Google News RSS: {e}", exc_info=True)
    
    return results


def scrape_duckduckgo_html(query: str = "political promises", max_results: int = 10) -> List[Dict]:
    """
    Scrape DuckDuckGo HTML search results.
    
    NOTE: This uses HTML scraping which is fragile. For production consider:
    - DuckDuckGo API (if available)
    - Bing News API
    - NewsAPI.org
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        List of dictionaries containing search results
    """
    results = []
    session = create_robust_session()
    
    try:
        # DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        
        logger.info(f"Scraping DuckDuckGo for query: {query}")
        
        response = session.get(search_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find search result elements (structure may change)
        result_divs = soup.find_all('div', class_='result', limit=max_results)
        
        if not result_divs:
            logger.warning("No results found in DuckDuckGo HTML")
            return results
        
        for div in result_divs:
            try:
                # Extract title and link
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem:
                    result = {
                        'title': title_elem.get_text(strip=True),
                        'description': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'source': 'DuckDuckGo',
                        'source_url': title_elem.get('href', ''),
                        'category': 'search',
                    }
                    results.append(result)
                    logger.debug(f"Scraped: {result['title'][:50]}...")
                    
            except Exception as e:
                logger.error(f"Error parsing DuckDuckGo result: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully scraped {len(results)} items from DuckDuckGo")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error scraping DuckDuckGo: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error scraping DuckDuckGo: {e}", exc_info=True)
    finally:
        session.close()
    
    return results


def scrape_reddit_json(subreddit: str = "politics", max_results: int = 10) -> List[Dict]:
    """
    Scrape Reddit using public JSON endpoint (no OAuth).
    
    NOTE: Reddit's public JSON is limited. For production:
    - Use Reddit API with OAuth
    - Respect rate limits (60 requests/minute for unauthenticated)
    - Consider using PRAW library
    
    Args:
        subreddit: Subreddit to scrape
        max_results: Maximum number of results to return
    
    Returns:
        List of dictionaries containing Reddit posts
    """
    results = []
    session = create_robust_session()
    
    try:
        # Reddit public JSON endpoint
        json_url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={max_results}"
        
        logger.info(f"Scraping Reddit r/{subreddit}")
        
        response = session.get(json_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' not in data or 'children' not in data['data']:
            logger.warning("Unexpected Reddit JSON structure")
            return results
        
        posts = data['data']['children']
        
        for post in posts:
            try:
                post_data = post.get('data', {})
                
                result = {
                    'title': post_data.get('title', 'No title'),
                    'description': post_data.get('selftext', '')[:500],  # Limit length
                    'source': f"Reddit r/{subreddit}",
                    'source_url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                    'category': 'social_media',
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                }
                results.append(result)
                logger.debug(f"Scraped: {result['title'][:50]}...")
                
            except Exception as e:
                logger.error(f"Error parsing Reddit post: {e}", exc_info=True)
                continue
        
        logger.info(f"Successfully scraped {len(results)} items from Reddit")
        
        # Be polite: add delay to avoid rate limiting
        time.sleep(1)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error scraping Reddit: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error scraping Reddit: {e}", exc_info=True)
    finally:
        session.close()
    
    return results


def scrape_all_sources(query: str = "political promises") -> List[Dict]:
    """
    Scrape all available sources and aggregate results.
    
    Args:
        query: Search query for news sources
    
    Returns:
        Aggregated list of results from all sources
    """
    logger.info("Starting scrape of all sources")
    
    all_results = []
    
    # Scrape each source
    all_results.extend(scrape_google_news_rss(query, max_results=5))
    all_results.extend(scrape_duckduckgo_html(query, max_results=5))
    all_results.extend(scrape_reddit_json("politics", max_results=5))
    
    logger.info(f"Total items scraped: {len(all_results)}")
    
    return all_results
