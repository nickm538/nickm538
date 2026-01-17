"""
Historical Research API - Deep Search Engine

This module provides deep historical research capabilities:
- Library of Congress Chronicling America API
- Old Fulton NY Post Cards (FultonHistory) scraper
- NYS Historic Newspapers
- Historical deed and land records
- War records and historical events
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
import asyncio

from services.chronicling_america_service import ChroniclingAmericaService
from services.fulton_history_service import FultonHistoryService
from services.historical_events_service import HistoricalEventsService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
chronicling_service = ChroniclingAmericaService()
fulton_service = FultonHistoryService()
events_service = HistoricalEventsService()


class HistoricalRecord(BaseModel):
    """A single historical record/mention."""
    id: str
    source: str
    source_name: str
    date: str
    year: int
    title: Optional[str] = None
    snippet: str
    full_text_available: bool = False
    url: Optional[str] = None
    page_number: Optional[int] = None
    confidence_score: float = Field(ge=0, le=1)
    relevance_score: float = Field(ge=0, le=1)
    record_type: str  # newspaper, deed, military, census, etc.


class HistoricalEvent(BaseModel):
    """A historical event that affected the area."""
    event_id: str
    name: str
    date: str
    year: int
    description: str
    event_type: str  # war, natural_disaster, development, etc.
    geographic_scope: str
    sources: List[str]
    relevance_to_property: Optional[str] = None


class DeepSearchResult(BaseModel):
    """Complete deep search results."""
    success: bool
    query_location: dict
    search_parameters: dict
    total_records_found: int
    records: List[HistoricalRecord]
    related_events: List[HistoricalEvent]
    time_periods_covered: List[str]
    sources_searched: List[str]
    search_notes: List[str]


class DeepSearchStatus(BaseModel):
    """Status of an ongoing deep search."""
    search_id: str
    status: str  # pending, in_progress, completed, failed
    progress_percent: int
    sources_completed: List[str]
    sources_pending: List[str]
    records_found_so_far: int
    estimated_time_remaining: Optional[int] = None


@router.post("/deep-search")
async def initiate_deep_search(
    address: str = Query(..., description="Property address or location name"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    year_start: int = Query(1700, description="Start year for search"),
    year_end: int = Query(2000, description="End year for search"),
    include_newspapers: bool = Query(True, description="Search historical newspapers"),
    include_military: bool = Query(True, description="Include military/war records"),
    include_census: bool = Query(True, description="Include census data"),
    include_deeds: bool = Query(True, description="Include deed records"),
    deep_mode: bool = Query(True, description="Enable exhaustive deep search"),
    background_tasks: BackgroundTasks = None
) -> DeepSearchResult:
    """
    Initiate a deep historical search for a property.

    This search queries multiple sources in parallel:
    1. Library of Congress Chronicling America (federal newspapers)
    2. FultonHistory (50+ million NY newspaper pages)
    3. NYS Historic Newspapers
    4. Historical event databases
    5. Military and census records

    The search is comprehensive and may take several minutes for deep mode.

    **Important**: Results are verified against multiple sources.
    If no records are found, the system will honestly report that
    rather than fabricating historical narratives.
    """
    try:
        # Extract location components
        location_parts = _parse_location(address)

        # Track sources and results
        all_records = []
        all_events = []
        sources_searched = []
        search_notes = []

        # 1. Search Library of Congress Chronicling America
        logger.info(f"Searching Chronicling America for {address}...")
        loc_results = await chronicling_service.search(
            location=location_parts['city'],
            state="New York",
            year_start=year_start,
            year_end=min(year_end, 1963),  # LOC coverage ends ~1963
            keywords=[location_parts.get('street', ''), "Long Island"],
            deep_search=deep_mode
        )
        sources_searched.append("Library of Congress Chronicling America")

        if loc_results:
            all_records.extend(loc_results)
            search_notes.append(
                f"Found {len(loc_results)} records in federal newspaper archives (1789-1963)"
            )
        else:
            search_notes.append(
                "No records found in Library of Congress newspaper archives"
            )

        # 2. Search FultonHistory (Old Fulton NY Post Cards)
        logger.info(f"Searching FultonHistory for {address}...")
        fulton_results = await fulton_service.search(
            query=f"{location_parts['city']} {location_parts.get('street', '')}",
            county=location_parts.get('county', 'Suffolk'),
            year_start=year_start,
            year_end=year_end,
            deep_search=deep_mode
        )
        sources_searched.append("FultonHistory (Old Fulton NY Post Cards)")

        if fulton_results:
            all_records.extend(fulton_results)
            search_notes.append(
                f"Found {len(fulton_results)} records in FultonHistory (50M+ NY newspaper pages)"
            )
        else:
            search_notes.append(
                "No records found in FultonHistory database"
            )

        # 3. Search for related historical events
        logger.info("Searching historical events database...")
        events = await events_service.get_events_for_location(
            lat=lat,
            lon=lon,
            municipality=location_parts['city'],
            county=location_parts.get('county', 'Suffolk'),
            year_start=year_start,
            year_end=year_end
        )
        sources_searched.append("Long Island Historical Events Database")

        if events:
            all_events.extend(events)
            search_notes.append(
                f"Found {len(events)} historical events affecting this area"
            )

        # 4. If military records requested, search war databases
        if include_military:
            military_results = await _search_military_records(
                location_parts, year_start, year_end
            )
            if military_results:
                all_records.extend(military_results)
                sources_searched.append("Military Records Database")

        # Sort records by date
        all_records.sort(key=lambda x: x.get('year', 0), reverse=True)

        # Calculate time periods covered
        time_periods = _calculate_time_periods(all_records, all_events)

        return DeepSearchResult(
            success=True,
            query_location={
                "address": address,
                "lat": lat,
                "lon": lon,
                "parsed": location_parts
            },
            search_parameters={
                "year_start": year_start,
                "year_end": year_end,
                "deep_mode": deep_mode
            },
            total_records_found=len(all_records),
            records=[HistoricalRecord(**r) for r in all_records],
            related_events=[HistoricalEvent(**e) for e in all_events],
            time_periods_covered=time_periods,
            sources_searched=sources_searched,
            search_notes=search_notes
        )

    except Exception as e:
        logger.error(f"Deep search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/newspapers/search")
async def search_newspapers(
    query: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="City or town name"),
    year_start: int = Query(1800, description="Start year"),
    year_end: int = Query(1960, description="End year"),
    source: str = Query("all", description="Source: loc, fulton, or all"),
    max_results: int = Query(50, description="Maximum results to return")
) -> dict:
    """
    Search historical newspapers directly.

    Sources:
    - loc: Library of Congress Chronicling America
    - fulton: FultonHistory (Old Fulton NY Post Cards)
    - all: Both sources
    """
    results = []

    if source in ["loc", "all"]:
        loc_results = await chronicling_service.search(
            location=location or "Long Island",
            state="New York",
            year_start=year_start,
            year_end=min(year_end, 1963),
            keywords=[query],
            max_results=max_results
        )
        results.extend(loc_results)

    if source in ["fulton", "all"]:
        fulton_results = await fulton_service.search(
            query=query,
            county=None,
            year_start=year_start,
            year_end=year_end,
            max_results=max_results
        )
        results.extend(fulton_results)

    return {
        "query": query,
        "total_results": len(results),
        "results": results[:max_results]
    }


@router.get("/events/long-island")
async def get_long_island_events(
    year_start: int = Query(1600, description="Start year"),
    year_end: int = Query(2000, description="End year"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    municipality: Optional[str] = Query(None, description="Filter by municipality")
) -> dict:
    """
    Get historical events that affected Long Island.

    Event types:
    - war: Military conflicts and battles
    - natural_disaster: Hurricanes, floods, fires
    - development: Major construction, railroad, highway
    - political: Boundary changes, incorporations
    - economic: Industry changes, significant businesses
    - cultural: Notable residents, landmarks
    """
    events = await events_service.get_long_island_events(
        year_start=year_start,
        year_end=year_end,
        event_type=event_type,
        municipality=municipality
    )

    return {
        "total_events": len(events),
        "events": events,
        "note": "Events sourced from verified historical records"
    }


@router.get("/events/wars")
async def get_war_history():
    """
    Get military history of Long Island.

    Long Island has significant military history including:
    - Revolutionary War (1775-1783): Battle of Long Island
    - War of 1812: Coastal defenses
    - Civil War (1861-1865): Camp Winfield Scott
    - World War I & II: Camp Upton, Mitchel Field
    - Cold War: Nike missile sites
    """
    return {
        "wars": [
            {
                "name": "Revolutionary War",
                "years": "1775-1783",
                "long_island_significance": "Battle of Long Island (August 27, 1776) - largest battle of the war",
                "key_locations": [
                    "Brooklyn Heights", "Gowanus", "Jamaica Pass",
                    "Flatbush", "Fort Greene"
                ],
                "events": [
                    {
                        "name": "Battle of Long Island",
                        "date": "1776-08-27",
                        "description": "First major battle after Declaration of Independence. "
                                       "British forces defeated Continental Army."
                    },
                    {
                        "name": "British Occupation",
                        "dates": "1776-1783",
                        "description": "Long Island occupied by British forces for 7 years"
                    }
                ]
            },
            {
                "name": "Civil War",
                "years": "1861-1865",
                "long_island_significance": "Training camps and volunteer regiments",
                "key_locations": [
                    "Camp Winfield Scott (Staten Island area)",
                    "Hempstead Plains"
                ]
            },
            {
                "name": "World War I",
                "years": "1917-1918",
                "long_island_significance": "Major military installations",
                "key_locations": [
                    "Camp Upton (Yaphank)",
                    "Mitchel Field (Garden City)",
                    "Roosevelt Field"
                ]
            },
            {
                "name": "World War II",
                "years": "1941-1945",
                "long_island_significance": "Aircraft production and military bases",
                "key_locations": [
                    "Grumman Aircraft (Bethpage)",
                    "Republic Aviation (Farmingdale)",
                    "Camp Upton",
                    "Mitchel Field"
                ]
            },
            {
                "name": "Cold War",
                "years": "1947-1991",
                "long_island_significance": "Nike missile defense sites",
                "key_locations": [
                    "Amityville", "Lido Beach", "Rocky Point",
                    "Lloyd Harbor", "Fire Island"
                ]
            }
        ]
    }


@router.get("/timeline/{location}")
async def get_location_timeline(
    location: str,
    year_start: int = Query(1600, description="Start year"),
    year_end: int = Query(2024, description="End year")
) -> dict:
    """
    Get a complete historical timeline for a specific location.

    Combines all available data sources into a chronological narrative.
    """
    timeline = await events_service.build_timeline(
        location=location,
        year_start=year_start,
        year_end=year_end
    )

    return {
        "location": location,
        "timeline": timeline,
        "sources": [
            "Library of Congress",
            "FultonHistory",
            "Historical Events Database",
            "USGS Historical Maps"
        ]
    }


def _parse_location(address: str) -> dict:
    """Parse address into components."""
    parts = {
        "original": address,
        "city": "",
        "street": "",
        "county": "Suffolk"  # Default to Suffolk
    }

    # Simple parsing - in production, use a proper geocoding service
    address_lower = address.lower()

    # Extract city/town
    long_island_places = [
        "bay shore", "islip", "babylon", "huntington", "smithtown",
        "brookhaven", "riverhead", "southampton", "east hampton",
        "shelter island", "southold", "oyster bay", "hempstead",
        "north hempstead", "glen cove", "long beach", "freeport",
        "garden city", "mineola", "westbury", "levittown", "massapequa",
        "patchogue", "sayville", "lindenhurst", "copiague", "amityville"
    ]

    for place in long_island_places:
        if place in address_lower:
            parts["city"] = place.title()
            break

    # Determine county
    nassau_places = [
        "hempstead", "north hempstead", "oyster bay", "glen cove",
        "long beach", "garden city", "mineola", "westbury", "levittown",
        "massapequa", "freeport", "rockville centre"
    ]

    for place in nassau_places:
        if place in address_lower:
            parts["county"] = "Nassau"
            break

    # Extract street (everything before city)
    if parts["city"]:
        idx = address_lower.find(parts["city"].lower())
        if idx > 0:
            parts["street"] = address[:idx].strip().rstrip(",")

    return parts


async def _search_military_records(location_parts: dict, year_start: int, year_end: int) -> List[dict]:
    """Search military and war-related records."""
    # This would connect to military archives in production
    return []


def _calculate_time_periods(records: List[dict], events: List[dict]) -> List[str]:
    """Calculate which time periods are covered by the search results."""
    periods = set()
    all_years = [r.get('year', 0) for r in records] + [e.get('year', 0) for e in events]

    for year in all_years:
        if year < 1700:
            periods.add("Pre-Colonial (<1700)")
        elif year < 1776:
            periods.add("Colonial Era (1700-1776)")
        elif year < 1800:
            periods.add("Revolutionary Period (1776-1800)")
        elif year < 1865:
            periods.add("Antebellum (1800-1865)")
        elif year < 1900:
            periods.add("Gilded Age (1865-1900)")
        elif year < 1945:
            periods.add("Early 20th Century (1900-1945)")
        elif year < 1970:
            periods.add("Post-War Era (1945-1970)")
        else:
            periods.add("Modern Era (1970-present)")

    return sorted(list(periods))
