"""
Historical Maps API - Basemap Overlays and Fire Insurance Maps

This module provides access to:
- Historical territorial maps (100 BC to present)
- Sanborn Fire Insurance Maps
- Historical boundary overlays
- Native American territory maps
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.sanborn_service import SanbornMapService
from services.historical_basemap_service import HistoricalBasemapService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
sanborn_service = SanbornMapService()
basemap_service = HistoricalBasemapService()


class MapLayer(BaseModel):
    """A map layer that can be displayed on the frontend."""
    layer_id: str
    name: str
    description: str
    layer_type: str  # tile, wms, geojson, image
    url: str
    year: Optional[int] = None
    year_range: Optional[str] = None
    attribution: str
    opacity: float = 0.7
    z_index: int = 1
    bounds: Optional[dict] = None
    metadata: Optional[dict] = None


class SanbornMap(BaseModel):
    """Sanborn Fire Insurance Map information."""
    map_id: str
    city: str
    county: str
    year: int
    volume: Optional[str] = None
    sheet: Optional[str] = None
    coverage_area: str
    url: str
    thumbnail_url: Optional[str] = None
    notes: Optional[str] = None


class HistoricalPeriod(BaseModel):
    """A historical period with associated map layers."""
    period_id: str
    name: str
    year_start: int
    year_end: int
    description: str
    layers: List[MapLayer]
    key_events: List[str]


@router.get("/sanborn/available")
async def get_available_sanborn_maps(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    municipality: Optional[str] = Query(None, description="City or town name")
) -> dict:
    """
    Get available Sanborn Fire Insurance Maps for a location.

    Sanborn maps are invaluable for understanding building history:
    - Building footprints and construction materials
    - Number of stories and building use
    - Fire walls and openings
    - Street names and addresses
    - Business names

    Sanborn coverage for Long Island varies by municipality and year.
    Major surveys were conducted 1884-1950.
    """
    try:
        available = await sanborn_service.get_available_maps(
            lat=lat,
            lon=lon,
            municipality=municipality
        )

        return {
            "location": {
                "lat": lat,
                "lon": lon,
                "municipality": municipality
            },
            "maps_available": len(available),
            "maps": [SanbornMap(**m) for m in available],
            "note": "Sanborn maps accessed via Library of Congress and ProQuest. "
                    "Some maps may require institutional access."
        }
    except Exception as e:
        logger.error(f"Error getting Sanborn maps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sanborn/{map_id}")
async def get_sanborn_map_details(map_id: str) -> dict:
    """
    Get detailed information and access URL for a specific Sanborn map.
    """
    try:
        details = await sanborn_service.get_map_details(map_id)

        if not details:
            raise HTTPException(status_code=404, detail="Sanborn map not found")

        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Sanborn details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-periods")
async def get_historical_periods() -> dict:
    """
    Get available historical map periods for Long Island.

    Returns a list of time periods with associated map layers.
    """
    return {
        "periods": [
            {
                "period_id": "pre_contact",
                "name": "Pre-Contact Era",
                "year_start": -100,
                "year_end": 1524,
                "description": "Long Island before European contact. "
                               "Home to the Lenape, Metoac, and Montaukett peoples.",
                "key_events": [
                    "Lenape and Metoac settlement",
                    "Wampum trade networks",
                    "Agricultural communities"
                ],
                "layers": [
                    {
                        "layer_id": "native_territories",
                        "name": "Native American Territories",
                        "description": "Approximate territories of indigenous peoples",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/native-territories",
                        "attribution": "Based on historical and archaeological research"
                    }
                ]
            },
            {
                "period_id": "dutch_colonial",
                "name": "Dutch Colonial Period",
                "year_start": 1624,
                "year_end": 1664,
                "description": "Dutch settlement and early colonial period",
                "key_events": [
                    "1624: First Dutch settlers",
                    "1636: First English settlements in eastern Long Island",
                    "1645: Purchase of land from Native Americans"
                ],
                "layers": [
                    {
                        "layer_id": "dutch_settlements",
                        "name": "Dutch Settlements c.1650",
                        "description": "Known Dutch settlement locations",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/dutch-settlements",
                        "attribution": "Historical records and archaeological data"
                    }
                ]
            },
            {
                "period_id": "english_colonial",
                "name": "English Colonial Period",
                "year_start": 1664,
                "year_end": 1776,
                "description": "English rule and colonial development",
                "key_events": [
                    "1664: English take control from Dutch",
                    "1683: Long Island divided into counties",
                    "1775: Revolutionary tensions"
                ],
                "layers": [
                    {
                        "layer_id": "colonial_towns",
                        "name": "Colonial Townships",
                        "description": "Town boundaries as established in colonial era",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/colonial-towns",
                        "attribution": "Historical maps and county records"
                    }
                ]
            },
            {
                "period_id": "revolutionary",
                "name": "Revolutionary War Era",
                "year_start": 1775,
                "year_end": 1783,
                "description": "Battle of Long Island and British occupation",
                "key_events": [
                    "August 27, 1776: Battle of Long Island",
                    "1776-1783: British occupation",
                    "Loyalist and Patriot properties"
                ],
                "layers": [
                    {
                        "layer_id": "battle_long_island",
                        "name": "Battle of Long Island",
                        "description": "Troop movements and battle sites",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/battle-long-island",
                        "attribution": "National Park Service"
                    }
                ]
            },
            {
                "period_id": "early_republic",
                "name": "Early Republic",
                "year_start": 1783,
                "year_end": 1860,
                "description": "Post-war development and agricultural era",
                "key_events": [
                    "1790: First federal census",
                    "1834: Long Island Rail Road founded",
                    "Agricultural and whaling economy"
                ],
                "layers": []
            },
            {
                "period_id": "civil_war",
                "name": "Civil War Era",
                "year_start": 1861,
                "year_end": 1865,
                "description": "Civil War period and Long Island's contribution",
                "key_events": [
                    "Long Island regiments formed",
                    "Camp Winfield Scott"
                ],
                "layers": []
            },
            {
                "period_id": "gilded_age",
                "name": "Gilded Age",
                "year_start": 1865,
                "year_end": 1900,
                "description": "Gold Coast estates and railroad expansion",
                "key_events": [
                    "Expansion of Long Island Rail Road",
                    "Construction of Gold Coast mansions",
                    "Development of resort communities"
                ],
                "layers": [
                    {
                        "layer_id": "lirr_1890",
                        "name": "LIRR Network c.1890",
                        "description": "Long Island Rail Road routes",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/lirr-1890",
                        "attribution": "Historical railroad maps"
                    }
                ]
            },
            {
                "period_id": "world_wars",
                "name": "World Wars Era",
                "year_start": 1914,
                "year_end": 1945,
                "description": "Military bases and aviation industry",
                "key_events": [
                    "Camp Upton established",
                    "Aviation industry growth",
                    "Grumman and Republic factories"
                ],
                "layers": [
                    {
                        "layer_id": "military_sites_ww2",
                        "name": "WWII Military Sites",
                        "description": "Military installations during WWII",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/military-ww2",
                        "attribution": "Historical military records"
                    }
                ]
            },
            {
                "period_id": "postwar",
                "name": "Post-War Suburbanization",
                "year_start": 1945,
                "year_end": 1970,
                "description": "Levittown and mass suburbanization",
                "key_events": [
                    "1947: Levittown construction begins",
                    "Highway construction",
                    "Population boom"
                ],
                "layers": [
                    {
                        "layer_id": "levittown_original",
                        "name": "Original Levittown Plan",
                        "description": "Original Levittown development",
                        "layer_type": "geojson",
                        "url": "/api/maps/geojson/levittown",
                        "attribution": "Historical development records"
                    }
                ]
            }
        ]
    }


@router.get("/geojson/{layer_id}")
async def get_geojson_layer(layer_id: str) -> dict:
    """
    Get GeoJSON data for a historical map layer.
    """
    try:
        geojson = await basemap_service.get_geojson_layer(layer_id)

        if not geojson:
            raise HTTPException(status_code=404, detail=f"Layer not found: {layer_id}")

        return geojson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting GeoJSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/native-territories")
async def get_native_territories() -> dict:
    """
    Get historical Native American territories on Long Island.

    Important note: Territory boundaries are approximate and based on
    historical records. These should not be considered definitive.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Metoac Confederation",
                    "description": "Collective term for 13 Algonquian-speaking tribes on Long Island",
                    "tribes": [
                        "Canarsie", "Rockaway", "Merrick", "Massapequa",
                        "Matinecock", "Nissequogue", "Setauket", "Unkechaug",
                        "Shinnecock", "Manhasset", "Secatogue", "Patchogue",
                        "Montaukett"
                    ],
                    "period": "Pre-contact to 1700s",
                    "source": "Historical and archaeological research"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-73.9, 40.8], [-73.7, 40.9], [-72.5, 41.0],
                        [-71.9, 41.1], [-71.9, 40.6], [-73.9, 40.5], [-73.9, 40.8]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Shinnecock Territory",
                    "description": "Traditional territory of the Shinnecock Nation",
                    "current_status": "Shinnecock Indian Nation - federally recognized 2010",
                    "reservation": "Shinnecock Reservation, Southampton"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-72.5, 40.85], [-72.3, 40.9], [-72.0, 40.85],
                        [-72.0, 40.75], [-72.5, 40.75], [-72.5, 40.85]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "name": "Montaukett Territory",
                    "description": "Traditional territory of the Montaukett people",
                    "note": "Montaukett are seeking state and federal recognition"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-72.0, 41.05], [-71.85, 41.08], [-71.85, 40.95],
                        [-72.0, 40.95], [-72.0, 41.05]
                    ]]
                }
            }
        ],
        "disclaimer": "Territory boundaries are approximate based on historical research. "
                      "For authoritative information, consult the respective tribal nations."
    }


@router.get("/tile-layers")
async def get_tile_layers() -> dict:
    """
    Get tile layer URLs for historical basemaps.
    """
    return {
        "layers": [
            {
                "id": "usgs_topo_current",
                "name": "USGS Topographic (Current)",
                "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
                "attribution": "USGS National Map",
                "max_zoom": 16
            },
            {
                "id": "usgs_imagery",
                "name": "USGS Imagery",
                "url": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
                "attribution": "USGS National Map",
                "max_zoom": 16
            },
            {
                "id": "nys_ortho_latest",
                "name": "NYS Latest Orthoimagery",
                "url": "https://orthos.its.ny.gov/arcgis/rest/services/wms/Latest/MapServer/tile/{z}/{y}/{x}",
                "attribution": "NYS GIS Program Office",
                "max_zoom": 20
            },
            {
                "id": "openstreetmap",
                "name": "OpenStreetMap",
                "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attribution": "OpenStreetMap contributors",
                "max_zoom": 19
            }
        ]
    }
