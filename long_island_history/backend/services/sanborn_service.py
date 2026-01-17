"""
Sanborn Map Service - Fire Insurance Maps Integration

Sanborn Fire Insurance Maps provide invaluable historical building data:
- Building footprints and materials
- Number of stories
- Building use
- Street names and addresses
- Business names

Sources:
- Library of Congress Digital Collections
- ProQuest (institutional access)
- Local library collections
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SanbornMapService:
    """Service for accessing Sanborn Fire Insurance Maps."""

    def __init__(self):
        # Library of Congress Sanborn Maps API
        self.loc_base_url = "https://www.loc.gov/collections/sanborn-maps"
        self.loc_api_url = "https://www.loc.gov/collections/sanborn-maps/"

        # Known Sanborn coverage for Long Island
        self.long_island_coverage = self._initialize_coverage()

        self.timeout = httpx.Timeout(30.0)

    def _initialize_coverage(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize known Sanborn map coverage for Long Island."""
        return {
            # Suffolk County
            "amityville": [
                {"year": 1893, "sheets": 2},
                {"year": 1898, "sheets": 3},
                {"year": 1904, "sheets": 4},
                {"year": 1910, "sheets": 5},
                {"year": 1921, "sheets": 8}
            ],
            "babylon": [
                {"year": 1886, "sheets": 1},
                {"year": 1893, "sheets": 2},
                {"year": 1898, "sheets": 3},
                {"year": 1910, "sheets": 4},
                {"year": 1921, "sheets": 6}
            ],
            "bay shore": [
                {"year": 1893, "sheets": 3},
                {"year": 1898, "sheets": 4},
                {"year": 1904, "sheets": 6},
                {"year": 1910, "sheets": 8},
                {"year": 1921, "sheets": 12},
                {"year": 1930, "sheets": 16}
            ],
            "huntington": [
                {"year": 1886, "sheets": 2},
                {"year": 1893, "sheets": 4},
                {"year": 1898, "sheets": 5},
                {"year": 1910, "sheets": 8},
                {"year": 1921, "sheets": 12}
            ],
            "islip": [
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3}
            ],
            "northport": [
                {"year": 1886, "sheets": 1},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3},
                {"year": 1921, "sheets": 4}
            ],
            "patchogue": [
                {"year": 1886, "sheets": 2},
                {"year": 1893, "sheets": 3},
                {"year": 1898, "sheets": 4},
                {"year": 1910, "sheets": 7},
                {"year": 1921, "sheets": 10}
            ],
            "port jefferson": [
                {"year": 1886, "sheets": 1},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3}
            ],
            "riverhead": [
                {"year": 1886, "sheets": 1},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3},
                {"year": 1921, "sheets": 5}
            ],
            "sag harbor": [
                {"year": 1884, "sheets": 2},
                {"year": 1898, "sheets": 3},
                {"year": 1910, "sheets": 3}
            ],
            "sayville": [
                {"year": 1893, "sheets": 2},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3}
            ],
            # Nassau County
            "freeport": [
                {"year": 1893, "sheets": 2},
                {"year": 1898, "sheets": 4},
                {"year": 1910, "sheets": 8},
                {"year": 1921, "sheets": 15},
                {"year": 1930, "sheets": 22}
            ],
            "glen cove": [
                {"year": 1886, "sheets": 2},
                {"year": 1893, "sheets": 3},
                {"year": 1898, "sheets": 4},
                {"year": 1910, "sheets": 7},
                {"year": 1921, "sheets": 10}
            ],
            "hempstead": [
                {"year": 1886, "sheets": 3},
                {"year": 1893, "sheets": 5},
                {"year": 1898, "sheets": 7},
                {"year": 1910, "sheets": 12},
                {"year": 1921, "sheets": 18}
            ],
            "long beach": [
                {"year": 1910, "sheets": 3},
                {"year": 1921, "sheets": 8},
                {"year": 1930, "sheets": 14}
            ],
            "mineola": [
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 4},
                {"year": 1921, "sheets": 7}
            ],
            "oyster bay": [
                {"year": 1886, "sheets": 1},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3}
            ],
            "rockville centre": [
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 5},
                {"year": 1921, "sheets": 9}
            ],
            "sea cliff": [
                {"year": 1893, "sheets": 2},
                {"year": 1898, "sheets": 2},
                {"year": 1910, "sheets": 3}
            ]
        }

    async def get_available_maps(
        self,
        lat: float,
        lon: float,
        municipality: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available Sanborn maps for a location.
        """
        available_maps = []

        # Find matching municipality
        if municipality:
            muni_key = municipality.lower()
            if muni_key in self.long_island_coverage:
                for map_info in self.long_island_coverage[muni_key]:
                    available_maps.append(
                        self._create_map_entry(municipality, map_info)
                    )

        # If no municipality specified, try to find nearby coverage
        if not available_maps:
            nearby = self._find_nearby_coverage(lat, lon)
            for muni, maps in nearby.items():
                for map_info in maps:
                    available_maps.append(
                        self._create_map_entry(muni.title(), map_info)
                    )

        return available_maps

    def _create_map_entry(self, municipality: str, map_info: dict) -> Dict[str, Any]:
        """Create a standardized map entry."""
        year = map_info["year"]

        return {
            "map_id": f"sanborn_{municipality.lower().replace(' ', '_')}_{year}",
            "city": municipality,
            "county": self._get_county(municipality),
            "year": year,
            "volume": "1",
            "sheet": f"1-{map_info.get('sheets', 1)}",
            "coverage_area": f"{municipality}, NY",
            "url": self._build_loc_url(municipality, year),
            "thumbnail_url": None,
            "notes": f"Sanborn Fire Insurance Map, {year}. {map_info.get('sheets', 1)} sheet(s)."
        }

    def _build_loc_url(self, municipality: str, year: int) -> str:
        """Build Library of Congress search URL."""
        query = f"{municipality} new york {year}"
        return f"https://www.loc.gov/collections/sanborn-maps/?q={query.replace(' ', '+')}"

    def _get_county(self, municipality: str) -> str:
        """Determine county from municipality name."""
        nassau_places = [
            "freeport", "glen cove", "hempstead", "long beach",
            "mineola", "oyster bay", "rockville centre", "sea cliff",
            "garden city", "great neck"
        ]

        if municipality.lower() in nassau_places:
            return "Nassau"
        return "Suffolk"

    def _find_nearby_coverage(self, lat: float, lon: float) -> Dict[str, List]:
        """Find Sanborn coverage near a location."""
        # Approximate coordinates for Long Island municipalities
        municipality_coords = {
            "bay shore": (40.7251, -73.2454),
            "babylon": (40.6956, -73.3257),
            "huntington": (40.8682, -73.4257),
            "patchogue": (40.7654, -73.0151),
            "riverhead": (40.9170, -72.6620),
            "freeport": (40.6576, -73.5832),
            "hempstead": (40.7062, -73.6187),
            "glen cove": (40.8623, -73.6332)
        }

        nearby = {}
        for muni, coords in municipality_coords.items():
            distance = ((lat - coords[0]) ** 2 + (lon - coords[1]) ** 2) ** 0.5
            if distance < 0.1:  # Approximately 10km
                if muni in self.long_island_coverage:
                    nearby[muni] = self.long_island_coverage[muni]

        return nearby

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_map_details(self, map_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific Sanborn map."""
        # Parse map_id
        parts = map_id.replace("sanborn_", "").rsplit("_", 1)
        if len(parts) != 2:
            return None

        municipality = parts[0].replace("_", " ").title()
        try:
            year = int(parts[1])
        except ValueError:
            return None

        # Look up in coverage database
        muni_key = municipality.lower()
        if muni_key not in self.long_island_coverage:
            return None

        map_info = None
        for info in self.long_island_coverage[muni_key]:
            if info["year"] == year:
                map_info = info
                break

        if not map_info:
            return None

        return {
            "map_id": map_id,
            "city": municipality,
            "county": self._get_county(municipality),
            "state": "New York",
            "year": year,
            "publisher": "Sanborn Map Company",
            "scale": "50 feet to 1 inch (typical)",
            "sheets": map_info.get("sheets", 1),
            "library_of_congress_url": self._build_loc_url(municipality, year),
            "proquest_note": "Full resolution images may be available through ProQuest Digital Sanborn Maps (institutional access required)",
            "interpretation_guide": {
                "pink": "Brick construction",
                "yellow": "Frame (wood) construction",
                "blue": "Stone construction",
                "brown": "Adobe or special construction",
                "green": "Iron or steel construction"
            },
            "usage_notes": (
                "Sanborn maps show building footprints, construction materials, "
                "number of stories, and building use. They are invaluable for "
                "understanding historical development patterns and individual "
                "building histories."
            ),
            "access_options": [
                {
                    "source": "Library of Congress",
                    "url": self._build_loc_url(municipality, year),
                    "access": "Free online",
                    "resolution": "Medium"
                },
                {
                    "source": "ProQuest Digital Sanborn Maps",
                    "url": "https://www.proquest.com/products-services/sanborn.html",
                    "access": "Subscription required (many libraries provide access)",
                    "resolution": "High"
                },
                {
                    "source": "Local Public Library",
                    "note": "Many Long Island libraries have physical Sanborn collections",
                    "access": "Free with library card"
                }
            ]
        }

    async def search_by_address(
        self,
        address: str,
        municipality: str,
        year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for Sanborn maps that might cover a specific address.

        Note: This doesn't search within maps (that requires OCR'd indexes),
        but identifies which map volumes would contain the address.
        """
        results = []

        muni_key = municipality.lower()
        if muni_key in self.long_island_coverage:
            maps = self.long_island_coverage[muni_key]

            if year:
                # Find closest year
                maps = sorted(maps, key=lambda x: abs(x["year"] - year))

            for map_info in maps[:5]:  # Return up to 5 maps
                results.append({
                    **self._create_map_entry(municipality, map_info),
                    "address_search_note": (
                        f"This {map_info['year']} Sanborn atlas covers {municipality}. "
                        f"Search within the {map_info['sheets']} sheet(s) to locate {address}. "
                        f"Sheets are typically organized by street name alphabetically."
                    )
                })

        return results

    def get_sanborn_legend(self) -> Dict[str, Any]:
        """Get Sanborn map color/symbol legend."""
        return {
            "colors": {
                "pink": "Brick construction",
                "yellow": "Frame (wood) construction",
                "blue": "Stone construction",
                "brown": "Adobe or special construction",
                "green": "Iron, steel, or concrete construction",
                "gray": "Fireproof construction"
            },
            "symbols": {
                "D": "Dwelling",
                "S": "Store",
                "O": "Office",
                "AUTO": "Automobile-related",
                "GAR": "Garage",
                "SHD": "Shed",
                "STABLE": "Stable/barn",
                "OP": "Open (no roof)",
                "SKY LT": "Skylight",
                "F.E.": "Fire escape",
                "F.A.": "Fire alarm"
            },
            "numbers": {
                "roof_number": "Number of stories",
                "basement": "B or BSMT indicates basement"
            }
        }
