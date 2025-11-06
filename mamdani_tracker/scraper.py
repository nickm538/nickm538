"""
News scraper module with robust HTTP handling.

Uses requests.Session with retry logic and proper error handling.
Scrapes from public sources (Google News RSS, DuckDuckGo HTML) without OAuth.

Note: For production use, consider using official APIs with proper authentication
for better reliability and compliance with terms of service.
"""
import logging
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# User-Agent to identify our scraper
USER_AGENT = 'MamdaniTracker/0.1 (Educational Project; +https://github.com/nickm538/nickm538)'

# Default timeout for all requests (connect timeout, read timeout)
DEFAULT_TIMEOUT = (5, 15)


def create_session():
    """
    Create a requests Session with retry logic and timeout.
    
    Returns:
        requests.Session: Configured session with retry policy
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # Only retry safe methods
    )
    
    # Mount the retry adapter
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers
    session.headers.update({
        'User-Agent': USER_AGENT
    })
    
    logger.info("Created HTTP session with retry policy")
    return session


def scrape_google_news_rss(query, max_results=10):
    """
    Scrape Google News RSS feed for a given query.
    
    Note: Google News RSS is a public feed but may have rate limits.
    For production, consider using Google News API with proper credentials.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of article dictionaries
    """
    articles = []
    session = create_session()
    
    try:
        # Google News RSS feed URL
        encoded_query = quote_plus(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Scraping Google News RSS for query: {query}")
        
        # Make request with timeout
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        # Parse RSS XML
        try:
            root = ET.fromstring(response.content)
            
            # Find all item elements
            items = root.findall('.//item')[:max_results]
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    
                    title = title_elem.text if title_elem is not None else "No title"
                    link = link_elem.text if link_elem is not None else ""
                    description = description_elem.text if description_elem is not None else ""
                    
                    # Parse date (RSS format: "Mon, 01 Jan 2025 12:00:00 GMT")
                    pub_date = None
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            from email.utils import parsedate_to_datetime
                            pub_date = parsedate_to_datetime(pub_date_elem.text)
                            # Convert to UTC if not already
                            if pub_date.tzinfo is None:
                                pub_date = pub_date.replace(tzinfo=timezone.utc)
                        except Exception as e:
                            logger.warning(f"Could not parse date '{pub_date_elem.text}': {e}")
                    
                    article = {
                        'title': title,
                        'url': link,
                        'source': 'Google News',
                        'snippet': description[:500] if description else "",  # Limit snippet length
                        'published_date': pub_date
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing RSS item: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} articles from Google News RSS")
            
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS XML: {e}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Google News RSS: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in scrape_google_news_rss: {e}")
    finally:
        session.close()
    
    return articles


def scrape_duckduckgo_html(query, max_results=10):
    """
    Scrape DuckDuckGo HTML search results.
    
    Note: This is a simple HTML scraper. DuckDuckGo may block excessive requests.
    Respect rate limits and consider adding delays between requests.
    For production, use proper search APIs with authentication.
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of article dictionaries
    """
    articles = []
    session = create_session()
    
    try:
        # DuckDuckGo HTML search URL
        encoded_query = quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        logger.info(f"Scraping DuckDuckGo HTML for query: {query}")
        
        # Make request with timeout
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find result elements (DuckDuckGo HTML structure)
        results = soup.find_all('div', class_='result', limit=max_results)
        
        for result in results:
            try:
                # Extract title and link
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    article = {
                        'title': title,
                        'url': link,
                        'source': 'DuckDuckGo',
                        'snippet': snippet[:500] if snippet else "",
                        'published_date': None  # DuckDuckGo HTML doesn't provide dates
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.warning(f"Error parsing DuckDuckGo result: {e}")
                continue
        
        logger.info(f"Found {len(articles)} articles from DuckDuckGo HTML")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching DuckDuckGo HTML: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in scrape_duckduckgo_html: {e}")
    finally:
        session.close()
    
    return articles


def scrape_reddit_json(subreddit, query, max_results=10):
    """
    Scrape Reddit JSON API for posts (public, no OAuth).
    
    Note: Reddit's public JSON API has rate limits and may require OAuth
    for reliable production use. Consider using PRAW with proper credentials.
    
    Args:
        subreddit (str): Subreddit name
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of article dictionaries
    """
    articles = []
    session = create_session()
    
    try:
        # Reddit JSON API endpoint (public, no auth)
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'limit': min(max_results, 25),  # Reddit limits to 25 per request
            'sort': 'relevance',
            'restrict_sr': 'on'
        }
        
        logger.info(f"Scraping Reddit JSON for query: {query} in r/{subreddit}")
        
        # Make request with timeout
        response = session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        
        # Parse JSON
        data = response.json()
        
        if 'data' in data and 'children' in data['data']:
            posts = data['data']['children']
            
            for post in posts[:max_results]:
                try:
                    post_data = post.get('data', {})
                    
                    title = post_data.get('title', 'No title')
                    url = f"https://reddit.com{post_data.get('permalink', '')}"
                    snippet = post_data.get('selftext', '')[:500]
                    
                    # Convert Unix timestamp to datetime (UTC)
                    created_utc = post_data.get('created_utc')
                    pub_date = None
                    if created_utc:
                        pub_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                    
                    article = {
                        'title': title,
                        'url': url,
                        'source': f'Reddit (r/{subreddit})',
                        'snippet': snippet,
                        'published_date': pub_date
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Reddit post: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} posts from Reddit")
        else:
            logger.warning("No posts found in Reddit JSON response")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Reddit JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in scrape_reddit_json: {e}")
    finally:
        session.close()
    
    return articles


def scrape_all_sources(query, max_per_source=5):
    """
    Scrape multiple sources and combine results.
    
    Includes small delays between requests to respect rate limits.
    
    Args:
        query (str): Search query
        max_per_source (int): Maximum results per source
        
    Returns:
        list: Combined list of articles from all sources
    """
    all_articles = []
    
    logger.info(f"Starting multi-source scrape for query: {query}")
    
    # Google News RSS
    try:
        articles = scrape_google_news_rss(query, max_per_source)
        all_articles.extend(articles)
        time.sleep(1)  # Rate limiting delay
    except Exception as e:
        logger.error(f"Error in Google News scraping: {e}")
    
    # DuckDuckGo HTML
    try:
        articles = scrape_duckduckgo_html(query, max_per_source)
        all_articles.extend(articles)
        time.sleep(1)  # Rate limiting delay
    except Exception as e:
        logger.error(f"Error in DuckDuckGo scraping: {e}")
    
    # Reddit (politics subreddit)
    try:
        articles = scrape_reddit_json('politics', query, max_per_source)
        all_articles.extend(articles)
        time.sleep(1)  # Rate limiting delay
    except Exception as e:
        logger.error(f"Error in Reddit scraping: {e}")
    
    logger.info(f"Scraped {len(all_articles)} total articles from all sources")
    return all_articles
