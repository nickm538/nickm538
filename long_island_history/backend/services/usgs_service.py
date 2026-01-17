"""
USGS Service - Historical Topographic Maps Integration

Provides access to:
- USGS Historical Topographic Map Collection
- 7.5-minute and 15-minute quadrangles
- Maps from 1880s to present
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class USGSService:
    """Service for retrieving USGS historical topographic maps."""

    def __init__(self):
        # USGS National Map APIs
        self.tnm_api_url = "https://tnmaccess.nationalmap.gov/api/v1"
        self.ngmdb_url = "https://ngmdb.usgs.gov/topoview"

        # Long Island quadrangle names
        self.long_island_quads = {
            # Suffolk County
            "ORIENT": {"lat": 41.1333, "lon": -72.3000},
            "GREENPORT": {"lat": 41.0833, "lon": -72.3500},
            "SOUTHOLD": {"lat": 41.0500, "lon": -72.4167},
            "MATTITUCK": {"lat": 41.0167, "lon": -72.5333},
            "RIVERHEAD": {"lat": 40.9333, "lon": -72.6667},
            "WADING RIVER": {"lat": 40.9500, "lon": -72.8333},
            "MIDDLE ISLAND": {"lat": 40.8833, "lon": -72.9500},
            "PORT JEFFERSON": {"lat": 40.9500, "lon": -73.0667},
            "SAINT JAMES": {"lat": 40.8667, "lon": -73.1500},
            "NORTHPORT": {"lat": 40.9000, "lon": -73.3333},
            "HUNTINGTON": {"lat": 40.8667, "lon": -73.4167},
            "LLOYD HARBOR": {"lat": 40.9167, "lon": -73.4500},
            "BAY SHORE EAST": {"lat": 40.7167, "lon": -73.2167},
            "BAY SHORE WEST": {"lat": 40.7167, "lon": -73.2833},
            "CENTRAL ISLIP": {"lat": 40.7833, "lon": -73.2000},
            "PATCHOGUE": {"lat": 40.7667, "lon": -73.0167},
            "BELLPORT": {"lat": 40.7500, "lon": -72.9333},
            "MORICHES": {"lat": 40.8000, "lon": -72.8167},
            "EASTPORT": {"lat": 40.8333, "lon": -72.7333},
            "QUOGUE": {"lat": 40.8167, "lon": -72.6167},
            "SOUTHAMPTON": {"lat": 40.8833, "lon": -72.3833},
            "SAG HARBOR": {"lat": 41.0000, "lon": -72.2833},
            "EAST HAMPTON": {"lat": 41.0000, "lon": -72.1833},
            "MONTAUK POINT": {"lat": 41.0667, "lon": -71.8667},
            # Nassau County
            "FREEPORT": {"lat": 40.6500, "lon": -73.5833},
            "JONES INLET": {"lat": 40.5833, "lon": -73.5667},
            "AMITYVILLE": {"lat": 40.6833, "lon": -73.4167},
            "HICKSVILLE": {"lat": 40.7667, "lon": -73.5167},
            "HUNTINGTON": {"lat": 40.8667, "lon": -73.4167},
            "SEA CLIFF": {"lat": 40.8500, "lon": -73.6500},
            "GLEN COVE": {"lat": 40.8667, "lon": -73.6333},
            "LYNBROOK": {"lat": 40.6500, "lon": -73.6833}
        }

        self.timeout = httpx.Timeout(30.0)

    async def get_available_maps(
        self,
        lat: float,
        lon: float
    ) -> List[Dict[str, Any]]:
        """
        Get available USGS topographic maps for a location.
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Query the TNM API for historical topos
                params = {
                    "datasets": "National Map 2.0",
                    "prodFormats": "GeoTIFF",
                    "polygon": self._create_search_polygon(lat, lon),
                    "outputFormat": "JSON"
                }

                response = await client.get(
                    f"{self.tnm_api_url}/products",
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_tnm_response(data)

        except Exception as e:
            logger.error(f"Error querying USGS API: {e}")

        # Return known historical map info for Long Island
        return self._get_known_historical_maps(lat, lon)

    def _create_search_polygon(self, lat: float, lon: float, buffer: float = 0.05) -> str:
        """Create a search polygon around a point."""
        coords = [
            [lon - buffer, lat - buffer],
            [lon + buffer, lat - buffer],
            [lon + buffer, lat + buffer],
            [lon - buffer, lat + buffer],
            [lon - buffer, lat - buffer]
        ]
        return str(coords)

    def _parse_tnm_response(self, data: dict) -> List[Dict[str, Any]]:
        """Parse TNM API response."""
        maps = []

        for item in data.get("items", []):
            maps.append({
                "layer_id": item.get("sourceId", ""),
                "name": item.get("title", ""),
                "description": item.get("abstract", ""),
                "year": self._extract_year(item.get("dateCreated", "")),
                "source": "USGS National Map",
                "coverage": item.get("mapName", ""),
                "tile_url": item.get("urls", {}).get("tiles"),
                "download_url": item.get("downloadURL")
            })

        return maps

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if date_str and len(date_str) >= 4:
            try:
                return int(date_str[:4])
            except ValueError:
                pass
        return None

    def _get_known_historical_maps(
        self,
        lat: float,
        lon: float
    ) -> List[Dict[str, Any]]:
        """Return known historical map information for Long Island."""
        # Determine which quadrangle(s) cover this location
        quad_name = self._find_quadrangle(lat, lon)

        base_maps = [
            {
                "layer_id": "usgs_topo_current",
                "name": "USGS US Topo (Current)",
                "description": "Current USGS topographic map",
                "year": 2023,
                "source": "USGS National Map",
                "coverage": quad_name or "Long Island",
                "tile_url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"
            },
            {
                "layer_id": "usgs_historical_1950s",
                "name": f"USGS 7.5-minute {quad_name} (1950s)",
                "description": "Historical 7.5-minute quadrangle from the 1950s",
                "year": 1955,
                "year_range": "1947-1960",
                "source": "USGS Historical Topographic Map Collection",
                "coverage": quad_name or "Long Island"
            },
            {
                "layer_id": "usgs_historical_1940s",
                "name": f"USGS 7.5-minute {quad_name} (1940s)",
                "description": "Historical wartime survey",
                "year": 1944,
                "year_range": "1940-1947",
                "source": "USGS Historical Topographic Map Collection",
                "coverage": quad_name or "Long Island"
            },
            {
                "layer_id": "usgs_historical_1900s",
                "name": f"USGS 15-minute {quad_name} (Early 1900s)",
                "description": "Early 20th century 15-minute series",
                "year": 1903,
                "year_range": "1897-1910",
                "source": "USGS Historical Topographic Map Collection",
                "coverage": quad_name or "Long Island"
            }
        ]

        return base_maps

    def _find_quadrangle(self, lat: float, lon: float) -> Optional[str]:
        """Find the USGS quadrangle name for a location."""
        min_dist = float('inf')
        closest_quad = None

        for name, center in self.long_island_quads.items():
            dist = ((lat - center["lat"]) ** 2 + (lon - center["lon"]) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_quad = name

        return closest_quad

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_topographic_map(
        self,
        lat: float,
        lon: float,
        year: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific historical topographic map.
        """
        quad_name = self._find_quadrangle(lat, lon)

        # Try to find the specific map
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Query historical topo collection
                params = {
                    "datasets": "Historical Topographic Maps",
                    "bbox": f"{lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}",
                    "dateType": "dateCreated",
                    "start": f"{year - 5}-01-01",
                    "end": f"{year + 5}-12-31",
                    "outputFormat": "JSON"
                }

                response = await client.get(
                    f"{self.tnm_api_url}/products",
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])

                    if items:
                        # Return best match
                        item = items[0]
                        return {
                            "map_id": item.get("sourceId"),
                            "map_name": item.get("title"),
                            "quadrangle_name": quad_name,
                            "year": self._extract_year(item.get("dateCreated")),
                            "scale": item.get("mapScale", "7.5-minute"),
                            "download_url": item.get("downloadURL"),
                            "thumbnail_url": item.get("previewGraphicURL")
                        }

        except Exception as e:
            logger.error(f"Error getting USGS map: {e}")

        # Return fallback info
        return {
            "map_id": f"usgs_{quad_name}_{year}",
            "map_name": f"USGS {quad_name} Quadrangle circa {year}",
            "quadrangle_name": quad_name,
            "year": year,
            "scale": "7.5-minute",
            "access_url": f"https://ngmdb.usgs.gov/topoview/viewer/#15/{lat}/{lon}",
            "note": "View this map on USGS TopoView"
        }

    def get_topoview_url(self, lat: float, lon: float, zoom: int = 15) -> str:
        """Get URL to view historical topos on USGS TopoView."""
        return f"https://ngmdb.usgs.gov/topoview/viewer/#{zoom}/{lat}/{lon}"
