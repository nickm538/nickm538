"""
Imagery Service - NYS GIS Orthoimagery Integration

Provides access to:
- Current NYS Orthoimagery (6-inch to 1-foot resolution)
- Historical aerial photography (1994-present)
- Leaf-off imagery for better ground visibility
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ImageryService:
    """Service for retrieving aerial imagery from NYS GIS."""

    def __init__(self):
        # NYS GIS Clearinghouse WMS/WMTS endpoints
        self.nys_base_url = "https://orthos.its.ny.gov/arcgis/rest/services/wms"

        # Available imagery years (Long Island coverage)
        self.available_years = {
            "Latest": {
                "url": f"{self.nys_base_url}/Latest/MapServer",
                "description": "Most recent statewide imagery",
                "resolution": "6-inch to 1-foot"
            },
            "2022": {
                "url": f"{self.nys_base_url}/2022/MapServer",
                "description": "2022 statewide 6-inch resolution",
                "resolution": "6-inch"
            },
            "2019": {
                "url": f"{self.nys_base_url}/2019/MapServer",
                "description": "2019 leaf-off imagery",
                "resolution": "1-foot"
            },
            "2016": {
                "url": f"{self.nys_base_url}/2016/MapServer",
                "description": "2016 statewide imagery",
                "resolution": "1-foot"
            },
            "2013": {
                "url": f"{self.nys_base_url}/2013/MapServer",
                "description": "2013 selected counties",
                "resolution": "1-foot"
            },
            "2010": {
                "url": f"{self.nys_base_url}/2010/MapServer",
                "description": "2010 imagery",
                "resolution": "1-foot"
            },
            "2008": {
                "url": f"{self.nys_base_url}/2008/MapServer",
                "description": "2008 imagery",
                "resolution": "1-foot"
            },
            "2004": {
                "url": f"{self.nys_base_url}/2004/MapServer",
                "description": "2004 Nassau/Suffolk",
                "resolution": "1-foot"
            },
            "2001": {
                "url": f"{self.nys_base_url}/2001/MapServer",
                "description": "2001 Long Island",
                "resolution": "2-foot"
            },
            "1994": {
                "url": f"{self.nys_base_url}/1994/MapServer",
                "description": "1994 first statewide digital",
                "resolution": "1-meter"
            }
        }

        self.timeout = httpx.Timeout(30.0)

    async def get_available_imagery(
        self,
        lat: float,
        lon: float
    ) -> List[Dict[str, Any]]:
        """
        Get list of available imagery for a location.

        Returns list of imagery layers sorted by year (newest first).
        """
        available = []

        for year, info in self.available_years.items():
            # Check if imagery is available at this location
            is_available = await self._check_imagery_availability(
                lat, lon, info["url"]
            )

            if is_available:
                available.append({
                    "layer_id": f"nys_ortho_{year.lower()}",
                    "name": f"NYS Orthoimagery {year}",
                    "description": info["description"],
                    "year": int(year) if year.isdigit() else 2024,
                    "resolution": info["resolution"],
                    "source": "NYS GIS Program Office",
                    "coverage": "New York State",
                    "wms_url": f"{info['url']}/WMSServer",
                    "tile_url": f"{info['url']}/tile/{{z}}/{{y}}/{{x}}"
                })

        # Sort by year descending
        available.sort(key=lambda x: x.get("year", 0), reverse=True)

        return available

    async def _check_imagery_availability(
        self,
        lat: float,
        lon: float,
        service_url: str
    ) -> bool:
        """Check if imagery is available at a location."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Query the service info
                response = await client.get(f"{service_url}?f=json")

                if response.status_code == 200:
                    data = response.json()
                    extent = data.get("fullExtent", {})

                    # Check if location is within service extent
                    xmin = extent.get("xmin", -180)
                    xmax = extent.get("xmax", 180)
                    ymin = extent.get("ymin", -90)
                    ymax = extent.get("ymax", 90)

                    # Note: Extent may be in Web Mercator, need to handle both
                    if abs(xmin) > 180:  # Web Mercator
                        return True  # Assume available for Long Island

                    return xmin <= lon <= xmax and ymin <= lat <= ymax

        except Exception as e:
            logger.debug(f"Error checking imagery availability: {e}")

        # Default to assuming available for Long Island
        return True

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_current_aerial(
        self,
        lat: float,
        lon: float,
        width: int = 1000,
        height: int = 1000,
        extent_meters: float = 200
    ) -> Dict[str, Any]:
        """
        Get current (latest) aerial imagery for a location.

        Returns WMS parameters for fetching the image.
        """
        # Calculate bounding box (approximate degrees from meters)
        # At Long Island's latitude, 1 degree ≈ 85km lat, 111km lon
        lat_extent = extent_meters / 111000
        lon_extent = extent_meters / 85000

        bbox = {
            "minx": lon - lon_extent,
            "miny": lat - lat_extent,
            "maxx": lon + lon_extent,
            "maxy": lat + lat_extent
        }

        wms_params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": "0",
            "styles": "",
            "crs": "EPSG:4326",
            "bbox": f"{bbox['miny']},{bbox['minx']},{bbox['maxy']},{bbox['maxx']}",
            "width": str(width),
            "height": str(height),
            "format": "image/jpeg"
        }

        return {
            "year": 2024,
            "wms_url": f"{self.available_years['Latest']['url']}/WMSServer",
            "wms_params": wms_params,
            "tile_url": f"{self.available_years['Latest']['url']}/tile/{{z}}/{{y}}/{{x}}",
            "export_url": self._build_export_url(lat, lon, width, height, extent_meters, "Latest")
        }

    async def get_historical_aerial(
        self,
        lat: float,
        lon: float,
        year: int,
        width: int = 1000,
        height: int = 1000,
        extent_meters: float = 200
    ) -> Optional[Dict[str, Any]]:
        """
        Get historical aerial imagery for a specific year.
        """
        # Find closest available year
        year_str = str(year)
        if year_str not in self.available_years:
            # Find closest year
            available_numeric = [int(y) for y in self.available_years.keys() if y.isdigit()]
            if not available_numeric:
                return None

            closest = min(available_numeric, key=lambda x: abs(x - year))
            year_str = str(closest)

        if year_str not in self.available_years:
            return None

        lat_extent = extent_meters / 111000
        lon_extent = extent_meters / 85000

        bbox = {
            "minx": lon - lon_extent,
            "miny": lat - lat_extent,
            "maxx": lon + lon_extent,
            "maxy": lat + lat_extent
        }

        wms_params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": "0",
            "styles": "",
            "crs": "EPSG:4326",
            "bbox": f"{bbox['miny']},{bbox['minx']},{bbox['maxy']},{bbox['maxx']}",
            "width": str(width),
            "height": str(height),
            "format": "image/jpeg"
        }

        return {
            "year": int(year_str),
            "wms_url": f"{self.available_years[year_str]['url']}/WMSServer",
            "wms_params": wms_params,
            "tile_url": f"{self.available_years[year_str]['url']}/tile/{{z}}/{{y}}/{{x}}"
        }

    def _build_export_url(
        self,
        lat: float,
        lon: float,
        width: int,
        height: int,
        extent_meters: float,
        year_key: str
    ) -> str:
        """Build ArcGIS REST export URL for direct image fetching."""
        lat_extent = extent_meters / 111000
        lon_extent = extent_meters / 85000

        bbox = f"{lon - lon_extent},{lat - lat_extent},{lon + lon_extent},{lat + lat_extent}"

        base_url = self.available_years[year_key]["url"]

        return (
            f"{base_url}/export?"
            f"bbox={bbox}&"
            f"bboxSR=4326&"
            f"size={width},{height}&"
            f"imageSR=4326&"
            f"format=jpg&"
            f"f=image"
        )

    def get_tile_layer_config(self, year: str = "Latest") -> Dict[str, Any]:
        """
        Get tile layer configuration for Leaflet/Mapbox.
        """
        if year not in self.available_years:
            year = "Latest"

        info = self.available_years[year]

        return {
            "url": f"{info['url']}/tile/{{z}}/{{y}}/{{x}}",
            "attribution": "NYS GIS Program Office",
            "maxZoom": 20,
            "minZoom": 10,
            "name": f"NYS Orthoimagery {year}",
            "description": info["description"]
        }
