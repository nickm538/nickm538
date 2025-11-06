"""
Web scraping and API integration for promise tracking
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import List, Dict, Tuple
import time


class PromiseScraper:
    """Scrapes news and social media for updates on Mamdani's promises"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.keywords = [
            'Zohran Mamdani',
            'Mamdani mayor',
            'NYC mayor elect',
            'New York City mayor'
        ]

    def scrape_all_sources(self) -> Tuple[List[Dict], int]:
        """
        Scrape all available sources for updates
        Returns: (list of articles, number of sources checked)
        """
        all_articles = []
        sources_checked = 0

        try:
            # Google News RSS
            google_articles = self.scrape_google_news()
            all_articles.extend(google_articles)
            sources_checked += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping Google News: {e}")

        try:
            # DuckDuckGo News (free, no API key)
            ddg_articles = self.scrape_duckduckgo_news()
            all_articles.extend(ddg_articles)
            sources_checked += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping DuckDuckGo: {e}")

        try:
            # NYC Government sites
            nyc_articles = self.scrape_nyc_official_sites()
            all_articles.extend(nyc_articles)
            sources_checked += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping NYC sites: {e}")

        try:
            # Reddit posts
            reddit_articles = self.scrape_reddit()
            all_articles.extend(reddit_articles)
            sources_checked += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping Reddit: {e}")

        # Deduplicate by URL
        unique_articles = []
        seen_urls = set()
        for article in all_articles:
            if article['url'] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article['url'])

        return unique_articles, sources_checked

    def scrape_google_news(self) -> List[Dict]:
        """Scrape Google News RSS feeds"""
        articles = []

        for keyword in ['Zohran+Mamdani', 'Mamdani+NYC+mayor']:
            try:
                url = f'https://news.google.com/rss/search?q={keyword}&hl=en-US&gl=US&ceid=US:en'
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:10]  # Limit to 10 per keyword

                    for item in items:
                        title_tag = item.find('title')
                        link_tag = item.find('link')
                        pub_date_tag = item.find('pubDate')
                        desc_tag = item.find('description')

                        articles.append({
                            'title': title_tag.get_text() if title_tag else '',
                            'url': link_tag.get_text() if link_tag else '',
                            'source': 'Google News',
                            'published': pub_date_tag.get_text() if pub_date_tag else '',
                            'summary': desc_tag.get_text() if desc_tag else ''
                        })
            except Exception as e:
                print(f"Error parsing Google News for {keyword}: {e}")

        return articles

    def scrape_duckduckgo_news(self) -> List[Dict]:
        """Scrape DuckDuckGo news (no API key required)"""
        articles = []

        try:
            # DuckDuckGo instant answer API (free, no auth)
            query = 'Zohran Mamdani NYC mayor'
            url = f'https://html.duckduckgo.com/html/?q={query.replace(" ", "+")}'

            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find news results
            results = soup.find_all('div', class_='result')[:15]

            for result in results:
                try:
                    link_tag = result.find('a', class_='result__a')
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        href = link_tag.get('href', '')

                        snippet_tag = result.find('a', class_='result__snippet')
                        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''

                        articles.append({
                            'title': title,
                            'url': href,
                            'source': 'DuckDuckGo',
                            'published': '',
                            'summary': snippet
                        })
                except Exception as e:
                    print(f"Error parsing DDG result: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping DuckDuckGo: {e}")

        return articles

    def scrape_nyc_official_sites(self) -> List[Dict]:
        """Scrape official NYC government sites"""
        articles = []

        sites = [
            'https://www.nyc.gov',
            'https://council.nyc.gov'
        ]

        for site in sites:
            try:
                # Search functionality on NYC sites
                search_url = f'{site}/search?q=Zohran+Mamdani'
                response = requests.get(search_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Generic search for links and headings
                    links = soup.find_all('a', href=True)

                    for link in links[:10]:
                        title = link.get_text(strip=True)
                        href = link['href']

                        if len(title) > 20 and 'mamdani' in title.lower():
                            full_url = href if href.startswith('http') else f'{site}{href}'

                            articles.append({
                                'title': title,
                                'url': full_url,
                                'source': 'NYC Official',
                                'published': '',
                                'summary': ''
                            })

            except Exception as e:
                print(f"Error scraping {site}: {e}")
                continue

        return articles

    def scrape_reddit(self) -> List[Dict]:
        """Scrape Reddit posts (using JSON API, no auth needed for reading)"""
        articles = []

        subreddits = ['nyc', 'newyorkcity', 'AskNYC']

        for subreddit in subreddits:
            try:
                url = f'https://www.reddit.com/r/{subreddit}/search.json?q=Zohran+Mamdani&sort=new&limit=10'
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    for post in data.get('data', {}).get('children', []):
                        post_data = post.get('data', {})

                        articles.append({
                            'title': post_data.get('title', ''),
                            'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                            'source': f'Reddit r/{subreddit}',
                            'published': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                            'summary': post_data.get('selftext', '')[:500]
                        })

                time.sleep(2)  # Be respectful to Reddit's rate limits

            except Exception as e:
                print(f"Error scraping Reddit r/{subreddit}: {e}")
                continue

        return articles

    def analyze_article_for_promise_update(self, article: Dict, promise) -> Dict:
        """
        Analyze an article to see if it contains updates about a specific promise
        Returns dict with: relevant (bool), sentiment, status_change
        """
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        promise_keywords = promise.title.lower().split()

        # Check relevance
        relevant_keywords = sum(1 for keyword in promise_keywords if keyword in text and len(keyword) > 3)
        is_relevant = relevant_keywords >= 2

        if not is_relevant:
            return {'relevant': False}

        # Detect sentiment and status
        sentiment = 'Neutral'
        status_change = None

        # Positive indicators
        positive_words = ['achieved', 'completed', 'delivered', 'success', 'approved', 'passed', 'implemented', 'signed']
        # Negative indicators
        negative_words = ['failed', 'rejected', 'blocked', 'opposed', 'cancelled', 'impossible', 'vetoed']
        # In-progress indicators
        progress_words = ['working on', 'progress', 'developing', 'discussing', 'planning', 'proposed']

        if any(word in text for word in positive_words):
            sentiment = 'Positive'
            status_change = 'Delivered'
        elif any(word in text for word in negative_words):
            sentiment = 'Negative'
            status_change = 'Failed'
        elif any(word in text for word in progress_words):
            sentiment = 'Positive'
            status_change = 'In Progress'

        return {
            'relevant': True,
            'sentiment': sentiment,
            'status_change': status_change,
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'source': article.get('source', ''),
            'summary': article.get('summary', '')
        }

    def get_initial_promises(self) -> List[Dict]:
        """
        Scrape initial campaign promises from various sources
        This is called once during setup
        """
        promises = []

        # Try to find campaign website and materials
        try:
            # Search for campaign promises
            articles = self.scrape_google_news()

            # Look for campaign platform documents
            for article in articles:
                if any(word in article['title'].lower() for word in ['platform', 'promise', 'pledge', 'plan', 'agenda']):
                    promises.append(article)

        except Exception as e:
            print(f"Error getting initial promises: {e}")

        return promises
