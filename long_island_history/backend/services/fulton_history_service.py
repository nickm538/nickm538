"""
Fulton History Service - Old Fulton NY Post Cards Scraper

FultonHistory.com contains 50+ million pages of NY historical newspapers,
including crucial Long Island sources not available elsewhere:
- The Suffolk County News
- The Long-Islander
- South Side Signal
- Babylon Signal
- And hundreds more

This scraper implements respectful web scraping with rate limiting.
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from bs4 import BeautifulSoup
import asyncio
import re
from urllib.parse import quote_plus
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class FultonHistoryService:
    """Service for searching FultonHistory (Old Fulton NY Post Cards)."""

    def __init__(self):
        self.base_url = "https://fultonhistory.com"
        self.search_url = f"{self.base_url}/Fulton.html"

        # Rate limiting settings - be respectful
        self.min_delay = 2.0  # Minimum seconds between requests
        self.last_request_time = 0

        self.timeout = httpx.Timeout(60.0)

        # Headers to mimic browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

        # Long Island newspaper titles to prioritize
        self.li_newspapers = [
            "Suffolk County News",
            "The Long-Islander",
            "South Side Signal",
            "Babylon Signal",
            "Corrector",
            "Sag Harbor Express",
            "East Hampton Star",
            "Southampton Press",
            "Riverhead News",
            "Port Jefferson Echo",
            "Patchogue Advance",
            "Bay Shore Sentinel",
            "Islip Press",
            "Northport Journal",
            "Huntington Long Islander",
            "Glen Cove Record-Pilot",
            "Nassau County Review",
            "Freeport Review",
            "Hempstead Sentinel",
            "Oyster Bay Guardian"
        ]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    async def search(
        self,
        query: str,
        county: Optional[str] = None,
        year_start: int = 1800,
        year_end: int = 2000,
        max_results: int = 50,
        deep_search: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search FultonHistory for historical newspaper mentions.

        Note: FultonHistory doesn't have a public API, so this uses
        web scraping. Be respectful of their servers.

        Args:
            query: Search query
            county: County filter (Suffolk or Nassau)
            year_start: Start year
            year_end: End year
            max_results: Maximum results to return
            deep_search: If True, try multiple query variations

        Returns:
            List of historical records found
        """
        all_results = []

        # Build search queries
        queries = self._build_queries(query, deep_search)

        for search_query in queries:
            try:
                # Rate limiting
                await self._rate_limit()

                results = await self._execute_search(
                    query=search_query,
                    county=county,
                    year_start=year_start,
                    year_end=year_end
                )

                all_results.extend(results)

                if len(all_results) >= max_results:
                    break

            except Exception as e:
                logger.error(f"FultonHistory search error: {e}")

        # Deduplicate and sort by relevance
        unique_results = self._deduplicate_results(all_results)

        return unique_results[:max_results]

    def _build_queries(self, query: str, deep_search: bool) -> List[str]:
        """Build list of search queries."""
        queries = [query]

        if deep_search:
            # Add variations
            clean_query = query.replace(",", " ").replace("NY", "").strip()

            # Try with Long Island context
            queries.append(f"{clean_query} Long Island")

            # Try exact phrase
            queries.append(f'"{clean_query}"')

            # Try individual significant words
            words = clean_query.split()
            for word in words:
                if len(word) > 4 and not word.isdigit():
                    queries.append(word)

        return list(set(queries))

    async def _rate_limit(self):
        """Implement rate limiting."""
        import time
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_delay:
            await asyncio.sleep(self.min_delay - elapsed)

        self.last_request_time = time.time()

    async def _execute_search(
        self,
        query: str,
        county: Optional[str],
        year_start: int,
        year_end: int
    ) -> List[Dict[str, Any]]:
        """Execute a search on FultonHistory."""
        results = []

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                follow_redirects=True
            ) as client:
                # FultonHistory uses a complex search interface
                # This is a simplified approach that may need adjustment

                # Build search URL (this may need updates based on site changes)
                encoded_query = quote_plus(query)
                search_params = {
                    "query": encoded_query,
                    "searchType": "phrase"
                }

                # Get search page
                response = await client.get(
                    self.search_url,
                    params=search_params
                )

                if response.status_code == 200:
                    results = self._parse_search_results(
                        response.text,
                        query,
                        year_start,
                        year_end,
                        county
                    )

        except Exception as e:
            logger.error(f"FultonHistory request error: {e}")
            # Return empty results rather than failing completely
            results = self._get_search_guidance(query)

        return results

    def _parse_search_results(
        self,
        html: str,
        query: str,
        year_start: int,
        year_end: int,
        county: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Parse search results from HTML."""
        results = []

        try:
            soup = BeautifulSoup(html, 'lxml')

            # Note: Actual parsing logic depends on FultonHistory's HTML structure
            # This is a placeholder that would need to be updated based on actual site

            # Look for result items
            result_items = soup.find_all('div', class_='result') or \
                           soup.find_all('tr', class_='result') or \
                           soup.find_all('li', class_='result')

            for item in result_items:
                record = self._parse_result_item(item, query)
                if record:
                    # Filter by year
                    if year_start <= record.get("year", 0) <= year_end:
                        # Filter by county if specified
                        if county:
                            if county.lower() in record.get("source_name", "").lower():
                                results.append(record)
                        else:
                            results.append(record)

        except Exception as e:
            logger.error(f"Error parsing FultonHistory results: {e}")

        return results

    def _parse_result_item(self, item, query: str) -> Optional[Dict[str, Any]]:
        """Parse a single result item."""
        try:
            # Extract text content
            text = item.get_text(strip=True)

            # Try to extract date
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\w+ \d{1,2}, \d{4})', text)
            date = date_match.group(1) if date_match else ""

            # Extract year
            year_match = re.search(r'\b(1[789]\d{2}|20[012]\d)\b', text)
            year = int(year_match.group(1)) if year_match else 0

            # Try to find newspaper name
            newspaper = "Unknown Long Island Newspaper"
            for paper in self.li_newspapers:
                if paper.lower() in text.lower():
                    newspaper = paper
                    break

            # Get link if available
            link = item.find('a')
            url = link.get('href', '') if link else ''

            return {
                "id": f"fulton_{hash(text) % 100000}",
                "source": "fulton_history",
                "source_name": newspaper,
                "date": date,
                "year": year,
                "title": newspaper,
                "snippet": text[:500] if len(text) > 500 else text,
                "full_text_available": True,
                "url": url if url.startswith('http') else f"{self.base_url}/{url}" if url else "",
                "page_number": 1,
                "confidence_score": 0.75,
                "relevance_score": self._calculate_relevance(text, query),
                "record_type": "newspaper"
            }

        except Exception as e:
            logger.error(f"Error parsing result item: {e}")
            return None

    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score."""
        text_lower = text.lower()
        query_lower = query.lower()

        score = 0.5

        # Query appears in text
        if query_lower in text_lower:
            score += 0.3

        # Long Island mention
        if "long island" in text_lower:
            score += 0.1

        # Known LI newspaper
        for paper in self.li_newspapers:
            if paper.lower() in text_lower:
                score += 0.1
                break

        return min(score, 1.0)

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results."""
        seen = set()
        unique = []

        for result in results:
            key = (result.get("date"), result.get("source_name"), result.get("snippet", "")[:100])
            if key not in seen:
                seen.add(key)
                unique.append(result)

        return unique

    def _get_search_guidance(self, query: str) -> List[Dict[str, Any]]:
        """Return guidance for manual search when automated search fails."""
        return [{
            "id": "fulton_manual_search",
            "source": "fulton_history",
            "source_name": "FultonHistory Manual Search Required",
            "date": "",
            "year": 0,
            "title": "Manual Search Recommended",
            "snippet": f"FultonHistory contains 50+ million pages of NY newspapers. "
                       f"For the most complete results, visit fultonhistory.com and "
                       f"search for: {query}",
            "full_text_available": False,
            "url": f"https://fultonhistory.com/Fulton.html",
            "page_number": 0,
            "confidence_score": 0.0,
            "relevance_score": 0.0,
            "record_type": "guidance"
        }]

    async def get_newspaper_list(self) -> List[Dict[str, Any]]:
        """Get list of Long Island newspapers in FultonHistory."""
        return [
            {"name": paper, "type": "newspaper", "region": "Long Island"}
            for paper in self.li_newspapers
        ]
