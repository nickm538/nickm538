"""
Parcel Data API - Suffolk & Nassau County GIS Integration

This module provides access to parcel data including:
- Section-Block-Lot (SBL) numbers
- Property boundaries (polygons)
- Owner information (public records)
- Deed references
- Tax assessment data
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
import httpx

from services.parcel_service import ParcelService
from services.geocoding_service import GeocodingService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
parcel_service = ParcelService()
geocoding_service = GeocodingService()


class ParcelBoundary(BaseModel):
    """GeoJSON representation of parcel boundary."""
    type: str = "Feature"
    geometry: dict
    properties: dict


class ParcelInfo(BaseModel):
    """Detailed parcel information."""
    sbl: str = Field(..., description="Section-Block-Lot number")
    address: str
    municipality: str
    county: str
    owner_name: Optional[str] = None
    acreage: Optional[float] = None
    land_use_code: Optional[str] = None
    land_use_description: Optional[str] = None
    year_built: Optional[int] = None
    assessed_value: Optional[float] = None
    deed_book: Optional[str] = None
    deed_page: Optional[str] = None
    deed_date: Optional[str] = None
    boundary: Optional[ParcelBoundary] = None
    centroid: Optional[dict] = None


class AddressSearchResult(BaseModel):
    """Address search result with coordinates."""
    address: str
    formatted_address: str
    lat: float
    lon: float
    county: str
    municipality: str
    confidence: float


class ParcelSearchResponse(BaseModel):
    """Response for parcel search."""
    success: bool
    message: str
    results: List[ParcelInfo]
    total_count: int


@router.get("/search/address")
async def search_by_address(
    address: str = Query(..., description="Street address to search"),
    include_boundary: bool = Query(True, description="Include parcel boundary polygon")
) -> ParcelSearchResponse:
    """
    Search for parcels by street address.

    This endpoint:
    1. Geocodes the address to coordinates
    2. Queries Suffolk/Nassau GIS for parcel data
    3. Returns SBL, boundaries, and property info
    """
    try:
        # First geocode the address
        location = await geocoding_service.geocode_address(address)

        if not location:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode address: {address}"
            )

        # Check if within Long Island bounds
        if not _is_within_long_island(location['lat'], location['lon']):
            raise HTTPException(
                status_code=400,
                detail="Address is outside Long Island coverage area"
            )

        # Query parcel data
        parcels = await parcel_service.get_parcel_by_location(
            lat=location['lat'],
            lon=location['lon'],
            include_boundary=include_boundary
        )

        return ParcelSearchResponse(
            success=True,
            message=f"Found {len(parcels)} parcel(s)",
            results=parcels,
            total_count=len(parcels)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching parcels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/coordinates")
async def search_by_coordinates(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    include_boundary: bool = Query(True, description="Include parcel boundary")
) -> ParcelSearchResponse:
    """
    Search for parcels by geographic coordinates.
    """
    if not _is_within_long_island(lat, lon):
        raise HTTPException(
            status_code=400,
            detail="Coordinates are outside Long Island coverage area"
        )

    try:
        parcels = await parcel_service.get_parcel_by_location(
            lat=lat,
            lon=lon,
            include_boundary=include_boundary
        )

        return ParcelSearchResponse(
            success=True,
            message=f"Found {len(parcels)} parcel(s)",
            results=parcels,
            total_count=len(parcels)
        )
    except Exception as e:
        logger.error(f"Error searching parcels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/sbl/{sbl}")
async def search_by_sbl(
    sbl: str,
    include_boundary: bool = Query(True, description="Include parcel boundary")
) -> ParcelSearchResponse:
    """
    Search for parcels by Section-Block-Lot (SBL) number.

    SBL Format varies by county:
    - Suffolk: Section-Block-Lot (e.g., "0200-001.00-01.00-001.000")
    - Nassau: Section-Block-Lot (e.g., "01-001-0001")
    """
    try:
        parcels = await parcel_service.get_parcel_by_sbl(
            sbl=sbl,
            include_boundary=include_boundary
        )

        if not parcels:
            raise HTTPException(
                status_code=404,
                detail=f"No parcel found with SBL: {sbl}"
            )

        return ParcelSearchResponse(
            success=True,
            message=f"Found parcel with SBL {sbl}",
            results=parcels,
            total_count=len(parcels)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching by SBL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deed-history/{sbl}")
async def get_deed_history(sbl: str):
    """
    Get deed transfer history for a parcel.

    Returns chronological list of property transfers including:
    - Grantor (seller)
    - Grantee (buyer)
    - Date of transfer
    - Consideration (sale price if available)
    - Deed book and page reference
    """
    try:
        history = await parcel_service.get_deed_history(sbl)

        return {
            "success": True,
            "sbl": sbl,
            "deed_history": history,
            "note": "Deed history obtained from county clerk records. "
                    "Older records may be incomplete."
        }
    except Exception as e:
        logger.error(f"Error getting deed history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/municipalities")
async def get_municipalities():
    """
    Get list of municipalities covered by this system.
    """
    return {
        "suffolk_county": {
            "towns": [
                "Babylon", "Brookhaven", "East Hampton", "Huntington",
                "Islip", "Riverhead", "Shelter Island", "Smithtown",
                "Southampton", "Southold"
            ],
            "villages": [
                "Amityville", "Asharoken", "Babylon", "Belle Terre",
                "Bellport", "Brightwaters", "Dering Harbor", "East Hampton",
                "Greenport", "Head of the Harbor", "Huntington Bay",
                "Islandia", "Lake Grove", "Lindenhurst", "Lloyd Harbor",
                "Mastic Beach", "Nissequogue", "North Haven", "Northport",
                "Ocean Beach", "Old Field", "Patchogue", "Poquott",
                "Port Jefferson", "Quogue", "Sag Harbor", "Sagaponack",
                "Saltaire", "Shoreham", "Southampton", "Westhampton Beach",
                "Westhampton Dunes"
            ]
        },
        "nassau_county": {
            "towns": ["Hempstead", "North Hempstead", "Oyster Bay"],
            "cities": ["Glen Cove", "Long Beach"],
            "villages": [
                "Atlantic Beach", "Baxter Estates", "Bayville",
                "Bellerose", "Brookville", "Cedarhurst", "Centre Island",
                "Cove Neck", "East Hills", "East Rockaway", "East Williston",
                "Farmingdale", "Floral Park", "Flower Hill", "Freeport",
                "Garden City", "Great Neck", "Great Neck Estates",
                "Great Neck Plaza", "Hempstead", "Hewlett Bay Park",
                "Hewlett Harbor", "Hewlett Neck", "Island Park",
                "Kensington", "Kings Point", "Lake Success", "Lattingtown",
                "Laurel Hollow", "Lawrence", "Lynbrook", "Malverne",
                "Manorhaven", "Massapequa Park", "Matinecock", "Mill Neck",
                "Mineola", "Muttontown", "New Hyde Park", "North Hills",
                "Old Brookville", "Old Westbury", "Oyster Bay Cove",
                "Plandome", "Plandome Heights", "Plandome Manor",
                "Port Washington North", "Rockville Centre", "Roslyn",
                "Roslyn Estates", "Roslyn Harbor", "Russell Gardens",
                "Saddle Rock", "Sands Point", "Sea Cliff", "South Floral Park",
                "Stewart Manor", "Thomaston", "Upper Brookville", "Valley Stream",
                "Westbury", "Williston Park", "Woodsburgh"
            ]
        }
    }


def _is_within_long_island(lat: float, lon: float) -> bool:
    """Check if coordinates are within Long Island bounds."""
    # Long Island approximate bounds
    BOUNDS = {
        "north": 41.1612,
        "south": 40.5431,
        "east": -71.8562,
        "west": -74.0421
    }
    return (
        BOUNDS["south"] <= lat <= BOUNDS["north"] and
        BOUNDS["west"] <= lon <= BOUNDS["east"]
    )
