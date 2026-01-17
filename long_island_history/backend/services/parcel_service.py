"""
Parcel Service - Suffolk & Nassau County GIS Integration

Connects to county GIS portals to retrieve:
- Parcel boundaries (polygons)
- Section-Block-Lot (SBL) numbers
- Property owner information
- Deed references
- Assessment data
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ParcelService:
    """Service for retrieving parcel data from county GIS systems."""

    def __init__(self):
        # Suffolk County GIS endpoints
        self.suffolk_base_url = "https://gis.suffolkcountyny.gov/arcgis/rest/services"
        self.suffolk_parcels_url = f"{self.suffolk_base_url}/Parcels/FeatureServer/0"

        # Nassau County GIS endpoints
        self.nassau_base_url = "https://gis.nassaucountyny.gov/arcgis/rest/services"
        self.nassau_parcels_url = f"{self.nassau_base_url}/Parcels/FeatureServer/0"

        # Suffolk County Open Data Portal
        self.suffolk_opendata_url = "https://opendata.suffolkcountyny.gov/api/v2"

        self.timeout = httpx.Timeout(30.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_parcel_by_location(
        self,
        lat: float,
        lon: float,
        include_boundary: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get parcel information for a geographic location.

        Queries both Suffolk and Nassau county GIS systems.
        """
        parcels = []

        # Determine which county based on approximate boundary
        # Nassau is roughly west of -73.4 longitude
        if lon > -73.4:
            # Query Nassau County
            nassau_parcels = await self._query_nassau_parcels(lat, lon, include_boundary)
            parcels.extend(nassau_parcels)
        else:
            # Query Suffolk County
            suffolk_parcels = await self._query_suffolk_parcels(lat, lon, include_boundary)
            parcels.extend(suffolk_parcels)

        return parcels

    async def _query_suffolk_parcels(
        self,
        lat: float,
        lon: float,
        include_boundary: bool
    ) -> List[Dict[str, Any]]:
        """Query Suffolk County GIS for parcel data."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use ArcGIS REST API query
                params = {
                    "f": "json",
                    "geometry": f"{lon},{lat}",
                    "geometryType": "esriGeometryPoint",
                    "spatialRel": "esriSpatialRelIntersects",
                    "outFields": "*",
                    "returnGeometry": str(include_boundary).lower(),
                    "outSR": "4326"
                }

                response = await client.get(
                    f"{self.suffolk_parcels_url}/query",
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_suffolk_response(data)
                else:
                    logger.warning(f"Suffolk GIS returned status {response.status_code}")
                    return await self._get_suffolk_fallback(lat, lon)

        except Exception as e:
            logger.error(f"Error querying Suffolk GIS: {e}")
            return await self._get_suffolk_fallback(lat, lon)

    async def _query_nassau_parcels(
        self,
        lat: float,
        lon: float,
        include_boundary: bool
    ) -> List[Dict[str, Any]]:
        """Query Nassau County GIS for parcel data."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "f": "json",
                    "geometry": f"{lon},{lat}",
                    "geometryType": "esriGeometryPoint",
                    "spatialRel": "esriSpatialRelIntersects",
                    "outFields": "*",
                    "returnGeometry": str(include_boundary).lower(),
                    "outSR": "4326"
                }

                response = await client.get(
                    f"{self.nassau_parcels_url}/query",
                    params=params
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_nassau_response(data)
                else:
                    logger.warning(f"Nassau GIS returned status {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Error querying Nassau GIS: {e}")
            return []

    def _parse_suffolk_response(self, data: dict) -> List[Dict[str, Any]]:
        """Parse Suffolk County GIS response into standardized format."""
        parcels = []

        for feature in data.get("features", []):
            attrs = feature.get("attributes", {})
            geometry = feature.get("geometry", {})

            parcel = {
                "sbl": attrs.get("SBL") or attrs.get("TAX_MAP_ID", ""),
                "address": self._format_address(attrs),
                "municipality": attrs.get("TOWN") or attrs.get("MUNICIPALITY", ""),
                "county": "Suffolk",
                "owner_name": attrs.get("OWNER") or attrs.get("OWNER_NAME"),
                "acreage": attrs.get("ACREAGE") or attrs.get("ACRES"),
                "land_use_code": attrs.get("PROP_CLASS") or attrs.get("LAND_USE"),
                "land_use_description": attrs.get("PROP_CLASS_DESC"),
                "year_built": attrs.get("YEAR_BUILT"),
                "assessed_value": attrs.get("TOTAL_ASSESSED_VALUE"),
                "deed_book": attrs.get("DEED_BOOK"),
                "deed_page": attrs.get("DEED_PAGE"),
                "deed_date": attrs.get("DEED_DATE"),
                "boundary": self._convert_geometry(geometry) if geometry else None,
                "centroid": {"lat": attrs.get("LAT"), "lon": attrs.get("LON")}
            }
            parcels.append(parcel)

        return parcels

    def _parse_nassau_response(self, data: dict) -> List[Dict[str, Any]]:
        """Parse Nassau County GIS response into standardized format."""
        parcels = []

        for feature in data.get("features", []):
            attrs = feature.get("attributes", {})
            geometry = feature.get("geometry", {})

            parcel = {
                "sbl": attrs.get("SBL") or attrs.get("PRINT_KEY", ""),
                "address": self._format_address(attrs),
                "municipality": attrs.get("CITY") or attrs.get("VILLAGE", ""),
                "county": "Nassau",
                "owner_name": attrs.get("OWNER"),
                "acreage": attrs.get("ACRES"),
                "land_use_code": attrs.get("PROP_CLASS"),
                "land_use_description": attrs.get("PROP_CLASS_DESC"),
                "year_built": attrs.get("YR_BLT"),
                "assessed_value": attrs.get("ASSESSED_VALUE"),
                "deed_book": attrs.get("DEED_BOOK"),
                "deed_page": attrs.get("DEED_PAGE"),
                "deed_date": attrs.get("DEED_DATE"),
                "boundary": self._convert_geometry(geometry) if geometry else None,
                "centroid": None
            }
            parcels.append(parcel)

        return parcels

    def _format_address(self, attrs: dict) -> str:
        """Format address from GIS attributes."""
        parts = []

        street_num = attrs.get("STREET_NUM") or attrs.get("HOUSE_NUMBER") or ""
        street_name = attrs.get("STREET_NAME") or attrs.get("STREET") or ""

        if street_num:
            parts.append(str(street_num))
        if street_name:
            parts.append(street_name)

        city = attrs.get("CITY") or attrs.get("TOWN") or ""
        if city:
            parts.append(city)

        return " ".join(parts) or attrs.get("ADDRESS", "")

    def _convert_geometry(self, geometry: dict) -> dict:
        """Convert ArcGIS geometry to GeoJSON format."""
        if "rings" in geometry:
            # Polygon geometry
            return {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": geometry["rings"]
                },
                "properties": {}
            }
        return None

    async def _get_suffolk_fallback(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Fallback method using Suffolk Open Data API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Query Suffolk Open Data Portal
                response = await client.get(
                    f"{self.suffolk_opendata_url}/parcels",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "format": "json"
                    }
                )

                if response.status_code == 200:
                    return response.json().get("parcels", [])

        except Exception as e:
            logger.error(f"Fallback query failed: {e}")

        return []

    async def get_parcel_by_sbl(
        self,
        sbl: str,
        include_boundary: bool = True
    ) -> List[Dict[str, Any]]:
        """Get parcel by Section-Block-Lot number."""
        # Determine county from SBL format
        if len(sbl.split("-")) == 4:
            # Suffolk format
            return await self._query_suffolk_by_sbl(sbl, include_boundary)
        else:
            # Nassau format
            return await self._query_nassau_by_sbl(sbl, include_boundary)

    async def _query_suffolk_by_sbl(
        self,
        sbl: str,
        include_boundary: bool
    ) -> List[Dict[str, Any]]:
        """Query Suffolk County by SBL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "f": "json",
                    "where": f"SBL = '{sbl}'",
                    "outFields": "*",
                    "returnGeometry": str(include_boundary).lower(),
                    "outSR": "4326"
                }

                response = await client.get(
                    f"{self.suffolk_parcels_url}/query",
                    params=params
                )

                if response.status_code == 200:
                    return self._parse_suffolk_response(response.json())

        except Exception as e:
            logger.error(f"Error querying by SBL: {e}")

        return []

    async def _query_nassau_by_sbl(
        self,
        sbl: str,
        include_boundary: bool
    ) -> List[Dict[str, Any]]:
        """Query Nassau County by SBL."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "f": "json",
                    "where": f"SBL = '{sbl}' OR PRINT_KEY = '{sbl}'",
                    "outFields": "*",
                    "returnGeometry": str(include_boundary).lower(),
                    "outSR": "4326"
                }

                response = await client.get(
                    f"{self.nassau_parcels_url}/query",
                    params=params
                )

                if response.status_code == 200:
                    return self._parse_nassau_response(response.json())

        except Exception as e:
            logger.error(f"Error querying Nassau by SBL: {e}")

        return []

    async def get_deed_history(self, sbl: str) -> List[Dict[str, Any]]:
        """
        Get deed transfer history for a parcel.

        Note: Full deed history requires access to county clerk records.
        This returns what's available through GIS/open data.
        """
        # This would connect to county clerk APIs if available
        # For now, return guidance on how to access records
        return [
            {
                "note": "Full deed history requires county clerk records",
                "suffolk_clerk": "https://www.suffolkcountyny.gov/Departments/County-Clerk/Land-Records",
                "nassau_clerk": "https://www.nassaucountyny.gov/1858/Nassau-County-Clerk",
                "recommendation": "Visit county clerk office for complete deed chain"
            }
        ]
