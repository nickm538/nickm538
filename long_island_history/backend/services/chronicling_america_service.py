"""
Chronicling America Service - Library of Congress Newspaper API

Provides access to:
- Digitized historical newspapers (1777-1963)
- Full-text search across millions of pages
- Free, no API key required
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio

logger = logging.getLogger(__name__)


class ChroniclingAmericaService:
    """Service for searching Library of Congress Chronicling America."""

    def __init__(self):
        self.base_url = "https://chroniclingamerica.loc.gov"
        self.search_url = f"{self.base_url}/search/pages/results/"
        self.timeout = httpx.Timeout(60.0)  # Long timeout for deep search

        # New York newspapers in the collection
        self.ny_newspapers = [
            {"lccn": "sn83030272", "title": "The Sun (New York)"},
            {"lccn": "sn83030214", "title": "New York Tribune"},
            {"lccn": "sn83030273", "title": "The Evening World"},
            {"lccn": "sn86071068", "title": "The Suffolk County News"},
            {"lccn": "sn83031566", "title": "The Long-Islander"},
            {"lccn": "sn84031477", "title": "Brooklyn Daily Eagle"},
        ]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30))
    async def search(
        self,
        location: str,
        state: str = "New York",
        year_start: int = 1800,
        year_end: int = 1963,
        keywords: Optional[List[str]] = None,
        max_results: int = 100,
        deep_search: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search Chronicling America for historical newspaper mentions.

        Args:
            location: City, town, or address to search for
            state: State name (default New York)
            year_start: Start year for search
            year_end: End year for search (max 1963)
            keywords: Additional keywords to include
            max_results: Maximum results to return
            deep_search: If True, search multiple variations

        Returns:
            List of historical records found
        """
        # Chronicling America coverage ends around 1963
        year_end = min(year_end, 1963)

        all_results = []

        # Build search queries
        queries = self._build_search_queries(location, keywords, deep_search)

        for query in queries:
            try:
                results = await self._execute_search(
                    query=query,
                    state=state,
                    year_start=year_start,
                    year_end=year_end,
                    max_results=max_results - len(all_results)
                )
                all_results.extend(results)

                if len(all_results) >= max_results:
                    break

                # Rate limiting - be nice to LOC servers
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Search error for query '{query}': {e}")

        # Deduplicate results
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result["id"] not in seen_ids:
                seen_ids.add(result["id"])
                unique_results.append(result)

        return unique_results[:max_results]

    def _build_search_queries(
        self,
        location: str,
        keywords: Optional[List[str]],
        deep_search: bool
    ) -> List[str]:
        """Build list of search queries."""
        queries = []

        # Primary query
        base_query = location
        if keywords:
            base_query = f"{location} {' '.join(keywords)}"
        queries.append(base_query)

        if deep_search:
            # Add variations for deep search
            # Remove common suffixes/prefixes
            location_clean = location.replace("NY", "").replace("New York", "").strip()

            # Try different formats
            variations = [
                location_clean,
                f'"{location_clean}"',  # Exact phrase
            ]

            # If it's an address, try just the street name
            parts = location_clean.split()
            if len(parts) > 1:
                # Remove house number if present
                if parts[0].isdigit():
                    street_name = " ".join(parts[1:])
                    variations.append(street_name)

            # Add Long Island context
            for var in variations:
                queries.append(f"{var} Long Island")

            queries.extend(variations)

        return list(set(queries))  # Remove duplicates

    async def _execute_search(
        self,
        query: str,
        state: str,
        year_start: int,
        year_end: int,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Execute a single search query."""
        results = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "proxtext": query,
                    "state": state,
                    "date1": year_start,
                    "date2": year_end,
                    "sequence": "",  # Any page
                    "rows": min(max_results, 50),  # API limit
                    "format": "json"
                }

                response = await client.get(self.search_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    total_items = data.get("totalItems", 0)

                    logger.info(f"Found {total_items} items for query: {query}")

                    for item in data.get("items", []):
                        record = self._parse_item(item, query)
                        if record:
                            results.append(record)

        except Exception as e:
            logger.error(f"Search execution error: {e}")

        return results

    def _parse_item(self, item: dict, query: str) -> Optional[Dict[str, Any]]:
        """Parse a Chronicling America search result item."""
        try:
            date = item.get("date", "")
            year = int(date[:4]) if date and len(date) >= 4 else 0

            # Extract OCR text snippet if available
            ocr_text = item.get("ocr_eng", "")
            snippet = self._extract_snippet(ocr_text, query) if ocr_text else ""

            return {
                "id": f"loc_{item.get('id', '')}",
                "source": "chronicling_america",
                "source_name": item.get("title", "Unknown Newspaper"),
                "date": date,
                "year": year,
                "title": item.get("title", ""),
                "snippet": snippet or f"Mentioned in {item.get('title', 'newspaper')} on {date}",
                "full_text_available": bool(ocr_text),
                "url": item.get("url", ""),
                "page_number": item.get("sequence", 1),
                "confidence_score": 0.85,  # LOC is reliable source
                "relevance_score": self._calculate_relevance(item, query),
                "record_type": "newspaper",
                "lccn": item.get("lccn", ""),
                "edition": item.get("edition", "")
            }
        except Exception as e:
            logger.error(f"Error parsing item: {e}")
            return None

    def _extract_snippet(self, text: str, query: str, context_chars: int = 200) -> str:
        """Extract a relevant snippet from OCR text."""
        text_lower = text.lower()
        query_lower = query.lower()

        # Find query in text
        idx = text_lower.find(query_lower)
        if idx == -1:
            # Try to find any word from the query
            for word in query_lower.split():
                if len(word) > 3:
                    idx = text_lower.find(word)
                    if idx != -1:
                        break

        if idx != -1:
            start = max(0, idx - context_chars // 2)
            end = min(len(text), idx + len(query) + context_chars // 2)
            snippet = text[start:end].strip()

            # Clean up snippet
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."

            return snippet

        # Return beginning of text if query not found
        return text[:context_chars] + "..." if len(text) > context_chars else text

    def _calculate_relevance(self, item: dict, query: str) -> float:
        """Calculate relevance score for a result."""
        score = 0.5  # Base score

        # Check if query appears in title
        title = item.get("title", "").lower()
        if query.lower() in title:
            score += 0.2

        # OCR text presence
        if item.get("ocr_eng"):
            score += 0.1

        # Prefer Long Island newspapers
        li_papers = ["long-islander", "suffolk", "nassau", "brooklyn"]
        for paper in li_papers:
            if paper in title:
                score += 0.1
                break

        return min(score, 1.0)

    async def get_newspaper_info(self, lccn: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific newspaper."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/lccn/{lccn}.json"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            logger.error(f"Error getting newspaper info: {e}")

        return None

    async def get_page_ocr(self, page_url: str) -> Optional[str]:
        """Get OCR text for a specific page."""
        try:
            # Convert page URL to OCR URL
            ocr_url = page_url.replace(".json", "/ocr.txt")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(ocr_url)

                if response.status_code == 200:
                    return response.text

        except Exception as e:
            logger.error(f"Error getting OCR text: {e}")

        return None
