"""
Geocoding Service - Address to Coordinates Conversion

Uses multiple geocoding providers with fallback:
1. Nominatim (OpenStreetMap) - free, no API key
2. US Census Geocoder - free, official
3. NY State Address Points - when available
"""

import logging
from typing import Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding addresses to coordinates."""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.census_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
        self.timeout = httpx.Timeout(15.0)

        # User agent for Nominatim (required)
        self.headers = {
            "User-Agent": "LongIslandHistoricalLandSystem/1.0"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address to coordinates.

        Returns dict with lat, lon, formatted_address, and confidence.
        Returns None if address cannot be geocoded.
        """
        # Ensure address includes Long Island context
        if "ny" not in address.lower() and "new york" not in address.lower():
            address = f"{address}, NY"

        # Try Census Geocoder first (more accurate for US addresses)
        result = await self._geocode_census(address)
        if result:
            return result

        # Fall back to Nominatim
        result = await self._geocode_nominatim(address)
        if result:
            return result

        logger.warning(f"Could not geocode address: {address}")
        return None

    async def _geocode_census(self, address: str) -> Optional[Dict[str, Any]]:
        """Use US Census Bureau geocoder."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "address": address,
                    "benchmark": "Public_AR_Current",
                    "format": "json"
                }

                response = await client.get(self.census_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    matches = data.get("result", {}).get("addressMatches", [])

                    if matches:
                        match = matches[0]
                        coords = match.get("coordinates", {})

                        return {
                            "lat": coords.get("y"),
                            "lon": coords.get("x"),
                            "formatted_address": match.get("matchedAddress", address),
                            "confidence": 0.95,
                            "source": "US Census Bureau"
                        }

        except Exception as e:
            logger.error(f"Census geocoding error: {e}")

        return None

    async def _geocode_nominatim(self, address: str) -> Optional[Dict[str, Any]]:
        """Use Nominatim (OpenStreetMap) geocoder."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            ) as client:
                params = {
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "us",
                    "viewbox": "-74.1,-71.8,40.5,41.2",  # Long Island bounding box
                    "bounded": 1
                }

                response = await client.get(self.nominatim_url, params=params)

                if response.status_code == 200:
                    results = response.json()

                    if results:
                        result = results[0]

                        return {
                            "lat": float(result.get("lat")),
                            "lon": float(result.get("lon")),
                            "formatted_address": result.get("display_name", address),
                            "confidence": float(result.get("importance", 0.5)),
                            "source": "OpenStreetMap"
                        }

        except Exception as e:
            logger.error(f"Nominatim geocoding error: {e}")

        return None

    async def reverse_geocode(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to an address.
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers
            ) as client:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "format": "json"
                }

                response = await client.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params=params
                )

                if response.status_code == 200:
                    result = response.json()

                    address = result.get("address", {})

                    return {
                        "formatted_address": result.get("display_name", ""),
                        "street": f"{address.get('house_number', '')} {address.get('road', '')}".strip(),
                        "city": address.get("city") or address.get("town") or address.get("village", ""),
                        "county": address.get("county", "").replace(" County", ""),
                        "state": address.get("state", ""),
                        "zip": address.get("postcode", "")
                    }

        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")

        return None

    async def validate_long_island_location(
        self,
        lat: float,
        lon: float
    ) -> Dict[str, Any]:
        """
        Validate that coordinates are within Long Island.
        """
        # Long Island bounds
        BOUNDS = {
            "north": 41.1612,
            "south": 40.5431,
            "east": -71.8562,
            "west": -74.0421
        }

        is_valid = (
            BOUNDS["south"] <= lat <= BOUNDS["north"] and
            BOUNDS["west"] <= lon <= BOUNDS["east"]
        )

        # Determine county
        county = None
        if is_valid:
            if lon > -73.4:
                county = "Nassau"
            else:
                county = "Suffolk"

        return {
            "is_valid": is_valid,
            "county": county,
            "message": "Within Long Island" if is_valid else "Outside Long Island coverage area"
        }
