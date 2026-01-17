"""
Imagery API - NYS GIS & USGS Historical Maps Integration

This module provides access to:
- Current aerial/orthoimagery from NYS GIS (1994-present)
- Historical USGS topographic maps
- Historical aerial photography
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
import httpx

from services.imagery_service import ImageryService
from services.usgs_service import USGSService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
imagery_service = ImageryService()
usgs_service = USGSService()


class ImageryMetadata(BaseModel):
    """Metadata for an imagery layer."""
    layer_id: str
    name: str
    description: str
    year: Optional[int] = None
    year_range: Optional[str] = None
    resolution: Optional[str] = None
    source: str
    coverage: str
    wms_url: Optional[str] = None
    tile_url: Optional[str] = None


class ImageryResponse(BaseModel):
    """Response containing imagery data or URL."""
    success: bool
    message: str
    imagery_type: str
    year: Optional[int] = None
    image_url: Optional[str] = None
    wms_params: Optional[dict] = None
    metadata: Optional[ImageryMetadata] = None


class AvailableImageryResponse(BaseModel):
    """List of available imagery for a location."""
    lat: float
    lon: float
    available_imagery: List[ImageryMetadata]


@router.get("/available")
async def get_available_imagery(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
) -> AvailableImageryResponse:
    """
    Get list of all available imagery for a location.

    Returns aerial photos and maps available for the given coordinates,
    sorted by date from newest to oldest.
    """
    try:
        available = await imagery_service.get_available_imagery(lat, lon)
        usgs_available = await usgs_service.get_available_maps(lat, lon)

        all_imagery = available + usgs_available
        all_imagery.sort(key=lambda x: x.get('year', 0), reverse=True)

        return AvailableImageryResponse(
            lat=lat,
            lon=lon,
            available_imagery=[
                ImageryMetadata(**img) for img in all_imagery
            ]
        )
    except Exception as e:
        logger.error(f"Error getting available imagery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_imagery(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    width: int = Query(1000, description="Image width in pixels"),
    height: int = Query(1000, description="Image height in pixels"),
    zoom_meters: float = Query(200, description="Approximate view extent in meters")
) -> ImageryResponse:
    """
    Get current (most recent) aerial imagery from NYS GIS.

    Returns WMS parameters for fetching the image directly or
    a pre-rendered image URL.
    """
    try:
        result = await imagery_service.get_current_aerial(
            lat=lat,
            lon=lon,
            width=width,
            height=height,
            extent_meters=zoom_meters
        )

        return ImageryResponse(
            success=True,
            message="Current aerial imagery available",
            imagery_type="orthophoto",
            year=result.get('year'),
            wms_params=result.get('wms_params'),
            metadata=ImageryMetadata(
                layer_id="nys_latest_ortho",
                name="NYS Latest Orthoimagery",
                description="Most recent leaf-off orthoimagery from NYS GIS Program",
                year=result.get('year'),
                resolution="6-inch to 1-foot",
                source="NYS GIS Clearinghouse",
                coverage="New York State",
                wms_url=result.get('wms_url')
            )
        )
    except Exception as e:
        logger.error(f"Error getting current imagery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical/{year}")
async def get_historical_imagery(
    year: int,
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    width: int = Query(1000, description="Image width"),
    height: int = Query(1000, description="Image height")
) -> ImageryResponse:
    """
    Get historical aerial imagery for a specific year.

    Available years vary by location. Use /available endpoint
    to see what's available for your area.

    Major NYS aerial photo programs:
    - 2022: Statewide 6-inch resolution
    - 2019: Statewide leaf-off
    - 2016: Statewide
    - 2013: Selected counties
    - 2008: Selected counties
    - 2004: Nassau/Suffolk
    - 2001: Long Island
    - 1994: First statewide digital
    """
    try:
        result = await imagery_service.get_historical_aerial(
            lat=lat,
            lon=lon,
            year=year,
            width=width,
            height=height
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No imagery available for year {year} at this location"
            )

        return ImageryResponse(
            success=True,
            message=f"Historical imagery from {year}",
            imagery_type="orthophoto",
            year=year,
            wms_params=result.get('wms_params'),
            image_url=result.get('image_url')
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting historical imagery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usgs-topo/{year}")
async def get_usgs_topographic(
    year: int,
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
) -> ImageryResponse:
    """
    Get USGS topographic map for a specific era.

    USGS has published topographic maps of Long Island since the 1890s.
    Major survey years include:
    - 1897-1903: First 15-minute series
    - 1940s: Wartime updates
    - 1950s-1960s: 7.5-minute series
    - 1970s-1990s: Updates
    """
    try:
        result = await usgs_service.get_topographic_map(
            lat=lat,
            lon=lon,
            year=year
        )

        if not result:
            return ImageryResponse(
                success=False,
                message=f"No USGS topographic map found for year {year}",
                imagery_type="topographic"
            )

        return ImageryResponse(
            success=True,
            message=f"USGS Topographic Map circa {year}",
            imagery_type="topographic",
            year=year,
            image_url=result.get('download_url'),
            metadata=ImageryMetadata(
                layer_id=result.get('map_id'),
                name=result.get('map_name'),
                description=f"USGS {result.get('scale', '7.5-minute')} quadrangle",
                year=year,
                source="USGS National Map",
                coverage=result.get('quadrangle_name')
            )
        )
    except Exception as e:
        logger.error(f"Error getting USGS map: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tile-urls")
async def get_tile_urls(
    layer: str = Query(..., description="Layer identifier")
):
    """
    Get tile URLs for map integration (Leaflet/Mapbox).

    Returns XYZ tile URL pattern for the specified layer.
    """
    tile_layers = {
        "nys_ortho_latest": {
            "url": "https://orthos.its.ny.gov/arcgis/rest/services/wms/Latest/MapServer/tile/{z}/{y}/{x}",
            "attribution": "NYS GIS Program Office",
            "maxZoom": 20,
            "minZoom": 10
        },
        "nys_ortho_2019": {
            "url": "https://orthos.its.ny.gov/arcgis/rest/services/wms/2019/MapServer/tile/{z}/{y}/{x}",
            "attribution": "NYS GIS Program Office",
            "maxZoom": 20,
            "minZoom": 10
        },
        "nys_ortho_2016": {
            "url": "https://orthos.its.ny.gov/arcgis/rest/services/wms/2016/MapServer/tile/{z}/{y}/{x}",
            "attribution": "NYS GIS Program Office",
            "maxZoom": 20,
            "minZoom": 10
        },
        "usgs_topo": {
            "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
            "attribution": "USGS National Map",
            "maxZoom": 16,
            "minZoom": 1
        },
        "usgs_imagery": {
            "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
            "attribution": "USGS National Map",
            "maxZoom": 16,
            "minZoom": 1
        }
    }

    if layer not in tile_layers:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown layer: {layer}. Available: {list(tile_layers.keys())}"
        )

    return tile_layers[layer]


@router.get("/wms-capabilities")
async def get_wms_capabilities():
    """
    Get WMS service capabilities for NYS GIS services.

    Returns information about available WMS layers and their parameters.
    """
    return {
        "nys_orthoimagery": {
            "base_url": "https://orthos.its.ny.gov/arcgis/services/wms",
            "services": [
                {
                    "name": "Latest",
                    "url": "https://orthos.its.ny.gov/arcgis/services/wms/Latest/MapServer/WMSServer",
                    "description": "Most recent orthoimagery"
                },
                {
                    "name": "2022",
                    "url": "https://orthos.its.ny.gov/arcgis/services/wms/2022/MapServer/WMSServer",
                    "description": "2022 statewide 6-inch imagery"
                },
                {
                    "name": "2019",
                    "url": "https://orthos.its.ny.gov/arcgis/services/wms/2019/MapServer/WMSServer",
                    "description": "2019 leaf-off imagery"
                }
            ],
            "parameters": {
                "version": "1.3.0",
                "crs": "EPSG:4326",
                "format": "image/jpeg"
            }
        },
        "usgs_historical_topo": {
            "base_url": "https://tnmaccess.nationalmap.gov/api/v1",
            "description": "USGS Historical Topographic Map Collection",
            "api_docs": "https://apps.nationalmap.gov/tnmaccess/"
        }
    }
