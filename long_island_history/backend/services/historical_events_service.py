"""
Historical Events Service - Long Island Historical Events Database

Provides access to a curated database of historical events
that affected Long Island, including:
- Wars and battles
- Natural disasters
- Major developments
- Political changes
- Economic milestones
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HistoricalEventsService:
    """Service for accessing Long Island historical events."""

    def __init__(self):
        # Comprehensive database of Long Island historical events
        self.events = self._initialize_events_database()

    def _initialize_events_database(self) -> List[Dict[str, Any]]:
        """Initialize the historical events database."""
        return [
            # Pre-Colonial Era
            {
                "event_id": "native_settlement",
                "name": "Metoac Confederation Settlement",
                "date": "1000",
                "year": 1000,
                "description": "Algonquian-speaking peoples establish permanent settlements across Long Island. "
                               "The Metoac Confederation includes 13 tribes including the Montaukett, Shinnecock, "
                               "Unkechaug, and others.",
                "event_type": "cultural",
                "geographic_scope": "Long Island",
                "sources": ["Archaeological records", "Oral histories"],
                "affected_areas": ["All Long Island"]
            },
            # Dutch Colonial Period
            {
                "event_id": "dutch_arrival_1624",
                "name": "Dutch Colonization Begins",
                "date": "1624",
                "year": 1624,
                "description": "Dutch West India Company establishes presence in the region. "
                               "First European settlements on western Long Island.",
                "event_type": "political",
                "geographic_scope": "Western Long Island",
                "sources": ["Colonial records"],
                "affected_areas": ["Brooklyn", "Queens"]
            },
            {
                "event_id": "english_settlement_1640",
                "name": "English Settlement of Eastern Long Island",
                "date": "1640",
                "year": 1640,
                "description": "English settlers from New England establish Southampton, the first English "
                               "settlement in New York State.",
                "event_type": "political",
                "geographic_scope": "Eastern Long Island",
                "sources": ["Town records", "Colonial documents"],
                "affected_areas": ["Southampton", "East Hampton", "Southold"]
            },
            {
                "event_id": "brooklyn_1646",
                "name": "Breuckelen Established",
                "date": "1646",
                "year": 1646,
                "description": "Dutch establish the village of Breuckelen (Brooklyn), "
                               "named after Breukelen in the Netherlands.",
                "event_type": "political",
                "geographic_scope": "Brooklyn",
                "sources": ["Dutch colonial records"],
                "affected_areas": ["Brooklyn"]
            },
            # English Colonial Period
            {
                "event_id": "english_takeover_1664",
                "name": "English Conquest of New Netherland",
                "date": "1664-08-27",
                "year": 1664,
                "description": "English forces under the Duke of York take control of New Amsterdam "
                               "and all of Long Island. The colony is renamed New York.",
                "event_type": "political",
                "geographic_scope": "Long Island",
                "sources": ["Colonial records", "Treaty of Westminster"],
                "affected_areas": ["All Long Island"]
            },
            {
                "event_id": "counties_established_1683",
                "name": "Long Island Counties Established",
                "date": "1683",
                "year": 1683,
                "description": "Long Island is divided into three counties: Kings (Brooklyn), "
                               "Queens, and Suffolk. Nassau County would later be split from Queens in 1899.",
                "event_type": "political",
                "geographic_scope": "Long Island",
                "sources": ["Colonial legislation"],
                "affected_areas": ["All Long Island"]
            },
            # Revolutionary War
            {
                "event_id": "battle_long_island_1776",
                "name": "Battle of Long Island",
                "date": "1776-08-27",
                "year": 1776,
                "description": "The largest battle of the American Revolutionary War. British forces under General "
                               "Howe defeat Washington's Continental Army. American casualties include approximately "
                               "300 killed and 1,000 captured. This led to British occupation of Long Island for "
                               "the remainder of the war.",
                "event_type": "war",
                "geographic_scope": "Brooklyn/Western Long Island",
                "sources": ["Military records", "Historical accounts"],
                "affected_areas": ["Brooklyn", "Gowanus", "Flatbush", "Jamaica Pass"],
                "casualties": {"american": 1300, "british": 400}
            },
            {
                "event_id": "british_occupation_1776",
                "name": "British Occupation of Long Island",
                "date": "1776-09-01",
                "year": 1776,
                "description": "Following the Battle of Long Island, British forces occupy the entire island. "
                               "Many Patriot families flee; Loyalists remain. Occupation lasts 7 years.",
                "event_type": "war",
                "geographic_scope": "Long Island",
                "sources": ["Military records", "Civilian accounts"],
                "affected_areas": ["All Long Island"],
                "duration": "1776-1783"
            },
            {
                "event_id": "culper_spy_ring",
                "name": "Culper Spy Ring Operations",
                "date": "1778",
                "year": 1778,
                "description": "George Washington establishes the Culper Spy Ring, one of America's first "
                               "intelligence networks. Key operatives include Abraham Woodhull of Setauket "
                               "and Robert Townsend of Oyster Bay.",
                "event_type": "war",
                "geographic_scope": "Long Island",
                "sources": ["Washington's papers", "Historical research"],
                "affected_areas": ["Setauket", "Oyster Bay", "Manhattan"]
            },
            # 19th Century
            {
                "event_id": "lirr_founded_1834",
                "name": "Long Island Rail Road Founded",
                "date": "1834-04-24",
                "year": 1834,
                "description": "The Long Island Rail Road is chartered, becoming one of the oldest railroads "
                               "in America still operating under its original name. Initially planned as a "
                               "route to Boston via ferry connections.",
                "event_type": "development",
                "geographic_scope": "Long Island",
                "sources": ["Corporate records", "Newspaper accounts"],
                "affected_areas": ["All Long Island"]
            },
            {
                "event_id": "whaling_peak_1840s",
                "name": "Peak of Long Island Whaling Industry",
                "date": "1845",
                "year": 1845,
                "description": "Sag Harbor and Cold Spring Harbor reach peak of whaling activity. "
                               "Sag Harbor becomes one of the major whaling ports in the United States.",
                "event_type": "economic",
                "geographic_scope": "Eastern Long Island",
                "sources": ["Shipping records", "Economic data"],
                "affected_areas": ["Sag Harbor", "Cold Spring Harbor", "Greenport"]
            },
            {
                "event_id": "civil_war_1861",
                "name": "Civil War Mobilization",
                "date": "1861",
                "year": 1861,
                "description": "Long Island contributes numerous regiments to the Union Army. "
                               "Training camps are established, and local industry supports the war effort.",
                "event_type": "war",
                "geographic_scope": "Long Island",
                "sources": ["Military records", "Regimental histories"],
                "affected_areas": ["All Long Island"]
            },
            {
                "event_id": "gold_coast_1890s",
                "name": "Gold Coast Estate Era Begins",
                "date": "1890",
                "year": 1890,
                "description": "Wealthy industrialists begin building grand estates on the North Shore, "
                               "creating the 'Gold Coast'. Families include Vanderbilts, Whitneys, "
                               "Roosevelts, Morgans, and Guggenheims.",
                "event_type": "economic",
                "geographic_scope": "North Shore",
                "sources": ["Property records", "Social histories"],
                "affected_areas": ["Oyster Bay", "Glen Cove", "Roslyn", "Cold Spring Harbor", "Huntington"]
            },
            {
                "event_id": "nassau_county_1899",
                "name": "Nassau County Created",
                "date": "1899-01-01",
                "year": 1899,
                "description": "Nassau County is created from the eastern portion of Queens County. "
                               "This separation occurs as the western portion of Queens joins "
                               "New York City's consolidation.",
                "event_type": "political",
                "geographic_scope": "Nassau County",
                "sources": ["State legislation"],
                "affected_areas": ["Nassau County", "Queens"]
            },
            # 20th Century - World Wars
            {
                "event_id": "camp_upton_1917",
                "name": "Camp Upton Established",
                "date": "1917",
                "year": 1917,
                "description": "U.S. Army establishes Camp Upton in Yaphank for WWI training. "
                               "Irving Berlin, stationed here, writes 'Yip Yip Yaphank' including "
                               "'God Bless America' (not released until 1938).",
                "event_type": "war",
                "geographic_scope": "Central Long Island",
                "sources": ["Military records", "Historical accounts"],
                "affected_areas": ["Yaphank", "Upton", "Brookhaven"]
            },
            {
                "event_id": "aviation_pioneers_1910s",
                "name": "Long Island Aviation Pioneers",
                "date": "1910",
                "year": 1910,
                "description": "Hempstead Plains becomes center of American aviation. Glenn Curtiss "
                               "establishes flying school. Belmont Park hosts international air meets. "
                               "Roosevelt Field (later) and Mitchel Field are established.",
                "event_type": "development",
                "geographic_scope": "Nassau County",
                "sources": ["Aviation records", "Newspaper accounts"],
                "affected_areas": ["Hempstead", "Garden City", "Mineola"]
            },
            {
                "event_id": "lindbergh_1927",
                "name": "Lindbergh's Transatlantic Flight",
                "date": "1927-05-20",
                "year": 1927,
                "description": "Charles Lindbergh departs Roosevelt Field in the 'Spirit of St. Louis' "
                               "for the first solo nonstop transatlantic flight to Paris. "
                               "The field becomes famous worldwide.",
                "event_type": "cultural",
                "geographic_scope": "Nassau County",
                "sources": ["Aviation records", "News archives"],
                "affected_areas": ["Garden City", "Roosevelt Field"]
            },
            {
                "event_id": "hurricane_1938",
                "name": "Great Hurricane of 1938",
                "date": "1938-09-21",
                "year": 1938,
                "description": "The 'Long Island Express' hurricane strikes with Category 3 force. "
                               "Westhampton Beach is devastated; Dune Road is breached. "
                               "Approximately 50 deaths on Long Island, massive property damage.",
                "event_type": "natural_disaster",
                "geographic_scope": "Long Island",
                "sources": ["Weather records", "News archives"],
                "affected_areas": ["Westhampton Beach", "East End", "South Shore"],
                "casualties": {"deaths": 50, "injured": "hundreds"}
            },
            {
                "event_id": "grumman_wwii",
                "name": "Grumman Aircraft WWII Production",
                "date": "1942",
                "year": 1942,
                "description": "Grumman Aircraft in Bethpage becomes major producer of Navy fighters "
                               "(F4F Wildcat, F6F Hellcat, TBF Avenger). At peak, employs 25,000+ workers. "
                               "Republic Aviation in Farmingdale produces P-47 Thunderbolt.",
                "event_type": "war",
                "geographic_scope": "Nassau County",
                "sources": ["Corporate records", "Military contracts"],
                "affected_areas": ["Bethpage", "Farmingdale", "Calverton"]
            },
            # Post-War Era
            {
                "event_id": "levittown_1947",
                "name": "Levittown Construction Begins",
                "date": "1947",
                "year": 1947,
                "description": "Levitt & Sons begins construction of Levittown, America's first "
                               "mass-produced suburb. Originally 17,447 homes for returning WWII veterans. "
                               "Transforms potato farms into modern suburban development.",
                "event_type": "development",
                "geographic_scope": "Nassau County",
                "sources": ["Corporate records", "News archives"],
                "affected_areas": ["Levittown", "Hicksville", "Island Trees"]
            },
            {
                "event_id": "lie_construction",
                "name": "Long Island Expressway Construction",
                "date": "1955",
                "year": 1955,
                "description": "Construction of the Long Island Expressway (I-495) begins under "
                               "Robert Moses. Eventually extends from Manhattan to Riverhead, "
                               "transforming development patterns across Long Island.",
                "event_type": "development",
                "geographic_scope": "Long Island",
                "sources": ["State records", "Moses papers"],
                "affected_areas": ["All Long Island"]
            },
            {
                "event_id": "nike_missiles_1950s",
                "name": "Nike Missile Defense Sites",
                "date": "1954",
                "year": 1954,
                "description": "Cold War Nike missile defense sites are established across Long Island "
                               "as part of New York's air defense. Sites include Amityville, Lido Beach, "
                               "Rocky Point, and Lloyd Harbor.",
                "event_type": "war",
                "geographic_scope": "Long Island",
                "sources": ["Military records", "Cold War archives"],
                "affected_areas": ["Amityville", "Lido Beach", "Rocky Point", "Lloyd Harbor", "Fire Island"]
            },
            {
                "event_id": "brookhaven_lab_1947",
                "name": "Brookhaven National Laboratory Established",
                "date": "1947-01-31",
                "year": 1947,
                "description": "Brookhaven National Laboratory is established on the former Camp Upton site. "
                               "Becomes major nuclear and particle physics research facility. "
                               "Seven Nobel Prizes have been awarded for work done here.",
                "event_type": "development",
                "geographic_scope": "Suffolk County",
                "sources": ["BNL records", "Federal archives"],
                "affected_areas": ["Upton", "Brookhaven"]
            },
            # Modern Era
            {
                "event_id": "hurricane_gloria_1985",
                "name": "Hurricane Gloria",
                "date": "1985-09-27",
                "year": 1985,
                "description": "Hurricane Gloria makes landfall on western Long Island as a Category 1 hurricane. "
                               "Causes widespread power outages and damage but less than feared due to timing of landfall.",
                "event_type": "natural_disaster",
                "geographic_scope": "Long Island",
                "sources": ["Weather records", "News archives"],
                "affected_areas": ["All Long Island"]
            },
            {
                "event_id": "twa_flight_800_1996",
                "name": "TWA Flight 800 Crash",
                "date": "1996-07-17",
                "year": 1996,
                "description": "TWA Flight 800 explodes and crashes into the Atlantic Ocean off the coast "
                               "of East Moriches shortly after takeoff from JFK. All 230 aboard perished. "
                               "Investigation determined the cause was a fuel tank explosion.",
                "event_type": "tragedy",
                "geographic_scope": "Suffolk County",
                "sources": ["NTSB investigation", "News archives"],
                "affected_areas": ["East Moriches", "Atlantic Ocean"]
            },
            {
                "event_id": "hurricane_sandy_2012",
                "name": "Hurricane Sandy",
                "date": "2012-10-29",
                "year": 2012,
                "description": "Superstorm Sandy devastates the South Shore of Long Island. "
                               "Record storm surge causes massive flooding. Long Beach, Freeport, "
                               "Lindenhurst, and Fire Island communities severely impacted.",
                "event_type": "natural_disaster",
                "geographic_scope": "Long Island",
                "sources": ["Weather records", "FEMA data"],
                "affected_areas": ["Long Beach", "Freeport", "Lindenhurst", "Fire Island", "South Shore"]
            }
        ]

    async def get_events_for_location(
        self,
        lat: float,
        lon: float,
        municipality: str,
        county: str,
        year_start: int = 1600,
        year_end: int = 2024
    ) -> List[Dict[str, Any]]:
        """Get historical events that affected a specific location."""
        relevant_events = []

        for event in self.events:
            # Check year range
            if not (year_start <= event["year"] <= year_end):
                continue

            # Check if location is in affected areas
            affected = event.get("affected_areas", [])

            is_relevant = False

            # Check for direct municipality match
            if municipality and any(municipality.lower() in area.lower() for area in affected):
                is_relevant = True

            # Check for county match
            if county and any(county.lower() in area.lower() for area in affected):
                is_relevant = True

            # Check for "All Long Island" or "Long Island"
            if any("long island" in area.lower() or "all" in area.lower() for area in affected):
                is_relevant = True

            if is_relevant:
                relevant_events.append({
                    **event,
                    "relevance_to_property": self._calculate_relevance(event, municipality, county)
                })

        # Sort by year
        relevant_events.sort(key=lambda x: x["year"])

        return relevant_events

    def _calculate_relevance(self, event: dict, municipality: str, county: str) -> str:
        """Calculate how relevant an event is to a specific location."""
        affected = event.get("affected_areas", [])

        # Direct municipality mention
        if municipality and any(municipality.lower() in area.lower() for area in affected):
            return f"Directly affected {municipality}"

        # County-level
        if county and any(county.lower() in area.lower() for area in affected):
            return f"Affected {county} County area"

        # Island-wide
        return "Island-wide event affecting all of Long Island"

    async def get_long_island_events(
        self,
        year_start: int = 1600,
        year_end: int = 2024,
        event_type: Optional[str] = None,
        municipality: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all Long Island events with optional filtering."""
        filtered = []

        for event in self.events:
            # Year filter
            if not (year_start <= event["year"] <= year_end):
                continue

            # Event type filter
            if event_type and event.get("event_type") != event_type:
                continue

            # Municipality filter
            if municipality:
                affected = event.get("affected_areas", [])
                if not any(municipality.lower() in area.lower() for area in affected):
                    if not any("long island" in area.lower() or "all" in area.lower() for area in affected):
                        continue

            filtered.append(event)

        return sorted(filtered, key=lambda x: x["year"])

    async def build_timeline(
        self,
        location: str,
        year_start: int,
        year_end: int
    ) -> List[Dict[str, Any]]:
        """Build a timeline of events for a location."""
        events = await self.get_long_island_events(
            year_start=year_start,
            year_end=year_end,
            municipality=location
        )

        timeline = []
        for event in events:
            timeline.append({
                "date": event["date"],
                "year": event["year"],
                "title": event["name"],
                "description": event["description"],
                "type": event["event_type"],
                "sources": event.get("sources", [])
            })

        return timeline
