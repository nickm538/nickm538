"""
Historical Basemap Service - Territorial Maps and Overlays

Provides historical map overlays from 100 BC to present:
- Native American territories
- Colonial boundaries
- Township boundaries
- Battle maps
- Railroad development
"""

import logging
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)


class HistoricalBasemapService:
    """Service for historical basemap overlays."""

    def __init__(self):
        self.geojson_data = self._initialize_geojson_data()

    def _initialize_geojson_data(self) -> Dict[str, Any]:
        """Initialize GeoJSON data for historical layers."""
        return {
            "native-territories": self._create_native_territories(),
            "dutch-settlements": self._create_dutch_settlements(),
            "colonial-towns": self._create_colonial_towns(),
            "battle-long-island": self._create_battle_map(),
            "lirr-1890": self._create_lirr_1890(),
            "military-ww2": self._create_ww2_sites(),
            "levittown": self._create_levittown()
        }

    def _create_native_territories(self) -> Dict[str, Any]:
        """Create GeoJSON for Native American territories."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Canarsie",
                        "description": "Western Long Island (Brooklyn area)",
                        "period": "Pre-contact to 1650s"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-74.0, 40.65], [-73.9, 40.7], [-73.85, 40.65],
                            [-73.9, 40.58], [-74.0, 40.65]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Rockaway",
                        "description": "Rockaway Peninsula area",
                        "period": "Pre-contact to 1650s"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.95, 40.58], [-73.75, 40.6], [-73.75, 40.55],
                            [-73.95, 40.53], [-73.95, 40.58]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Matinecock",
                        "description": "North Shore, Oyster Bay to Huntington area",
                        "period": "Pre-contact to 1700s"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.6, 40.85], [-73.4, 40.9], [-73.3, 40.88],
                            [-73.3, 40.8], [-73.6, 40.78], [-73.6, 40.85]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Massapequa",
                        "description": "South Shore, Massapequa to Amityville",
                        "period": "Pre-contact to 1650s"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.5, 40.7], [-73.35, 40.7], [-73.35, 40.62],
                            [-73.5, 40.62], [-73.5, 40.7]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Setauket",
                        "description": "Central North Shore, Setauket area",
                        "period": "Pre-contact to 1700s"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.15, 40.92], [-72.95, 40.95], [-72.9, 40.88],
                            [-73.1, 40.85], [-73.15, 40.92]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Unkechaug",
                        "description": "Mastic area, Poospatuck Reservation today",
                        "period": "Pre-contact to present",
                        "status": "State-recognized tribe with reservation"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.88, 40.8], [-72.78, 40.82], [-72.75, 40.76],
                            [-72.85, 40.74], [-72.88, 40.8]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Shinnecock",
                        "description": "Southampton area",
                        "period": "Pre-contact to present",
                        "status": "Federally recognized tribe (2010) with reservation"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.5, 40.9], [-72.3, 40.92], [-72.25, 40.85],
                            [-72.45, 40.82], [-72.5, 40.9]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Montaukett",
                        "description": "Eastern tip of Long Island",
                        "period": "Pre-contact to present",
                        "status": "Seeking state and federal recognition"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.0, 41.05], [-71.85, 41.08], [-71.85, 40.95],
                            [-72.0, 40.93], [-72.0, 41.05]
                        ]]
                    }
                }
            ]
        }

    def _create_dutch_settlements(self) -> Dict[str, Any]:
        """Create GeoJSON for Dutch colonial settlements."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Breuckelen (Brooklyn)",
                        "established": 1646,
                        "description": "Named after Breukelen in the Netherlands"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9442, 40.6782]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Nieuw Amersfoort (Flatlands)",
                        "established": 1636,
                        "description": "Early Dutch farming settlement"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9245, 40.6165]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Midwout (Flatbush)",
                        "established": 1652,
                        "description": "Dutch agricultural village"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9580, 40.6520]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Boswijck (Bushwick)",
                        "established": 1661,
                        "description": "Dutch settlement"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.9212, 40.6944]
                    }
                }
            ]
        }

    def _create_colonial_towns(self) -> Dict[str, Any]:
        """Create GeoJSON for colonial-era township boundaries."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Southampton",
                        "established": 1640,
                        "description": "First English settlement in New York"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.6, 40.95], [-72.2, 41.0], [-72.0, 40.9],
                            [-72.0, 40.75], [-72.6, 40.7], [-72.6, 40.95]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Southold",
                        "established": 1640,
                        "description": "Founded by New Haven colonists"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.6, 41.1], [-72.0, 41.15], [-71.9, 41.05],
                            [-72.4, 40.95], [-72.6, 41.1]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "East Hampton",
                        "established": 1648,
                        "description": "English Puritan settlement"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-72.2, 41.05], [-71.85, 41.1], [-71.85, 40.92],
                            [-72.2, 40.88], [-72.2, 41.05]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Huntington",
                        "established": 1653,
                        "description": "English settlement"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.5, 40.92], [-73.25, 40.95], [-73.2, 40.75],
                            [-73.45, 40.72], [-73.5, 40.92]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Brookhaven",
                        "established": 1655,
                        "description": "Largest town by area in New York"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.2, 40.95], [-72.6, 41.0], [-72.6, 40.7],
                            [-73.1, 40.7], [-73.2, 40.95]
                        ]]
                    }
                }
            ]
        }

    def _create_battle_map(self) -> Dict[str, Any]:
        """Create GeoJSON for Battle of Long Island (1776)."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "British Landing at Gravesend",
                        "date": "August 22, 1776",
                        "description": "15,000 British troops land"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.98, 40.59]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Jamaica Pass",
                        "date": "August 27, 1776",
                        "description": "British flanking maneuver through unguarded pass"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.87, 40.7]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Battle of Gowanus",
                        "date": "August 27, 1776",
                        "description": "Maryland troops hold off British"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.99, 40.67]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Washington's Retreat",
                        "date": "August 29-30, 1776",
                        "description": "Continental Army evacuates across East River"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.99, 40.7]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "American Lines",
                        "description": "Defensive positions along Brooklyn Heights"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-74.0, 40.65], [-73.97, 40.68], [-73.94, 40.69]
                        ]
                    }
                }
            ]
        }

    def _create_lirr_1890(self) -> Dict[str, Any]:
        """Create GeoJSON for Long Island Rail Road network circa 1890."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Main Line",
                        "description": "Jamaica to Greenport",
                        "opened": 1844
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.8, 40.7], [-73.5, 40.75], [-73.2, 40.85],
                            [-72.9, 40.88], [-72.6, 40.92], [-72.35, 41.1]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Montauk Branch",
                        "description": "Jamaica to Montauk",
                        "opened": 1895
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.8, 40.7], [-73.5, 40.68], [-73.2, 40.73],
                            [-72.8, 40.78], [-72.3, 40.87], [-71.95, 41.05]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Oyster Bay Branch",
                        "opened": 1889
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.7, 40.75], [-73.6, 40.8], [-73.52, 40.87]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Port Jefferson Branch",
                        "opened": 1873
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-73.5, 40.77], [-73.35, 40.82], [-73.15, 40.92],
                            [-73.07, 40.93]
                        ]
                    }
                }
            ]
        }

    def _create_ww2_sites(self) -> Dict[str, Any]:
        """Create GeoJSON for WWII military sites."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Camp Upton",
                        "type": "Army Training Camp",
                        "description": "Induction and training center",
                        "now": "Brookhaven National Laboratory"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-72.87, 40.87]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Mitchel Field",
                        "type": "Army Air Forces Base",
                        "description": "Major air base"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.6, 40.73]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Grumman Aircraft",
                        "type": "Aircraft Manufacturing",
                        "description": "F6F Hellcat, TBF Avenger production"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.49, 40.76]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Republic Aviation",
                        "type": "Aircraft Manufacturing",
                        "description": "P-47 Thunderbolt production"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.44, 40.73]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Roosevelt Field",
                        "type": "Aviation History",
                        "description": "Lindbergh's 1927 departure point"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-73.62, 40.74]
                    }
                }
            ]
        }

    def _create_levittown(self) -> Dict[str, Any]:
        """Create GeoJSON for original Levittown development."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Levittown Original Bounds",
                        "established": 1947,
                        "homes": 17447,
                        "description": "America's first mass-produced suburb"
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-73.55, 40.74], [-73.48, 40.74],
                            [-73.48, 40.70], [-73.55, 40.70],
                            [-73.55, 40.74]
                        ]]
                    }
                }
            ]
        }

    async def get_geojson_layer(self, layer_id: str) -> Optional[Dict[str, Any]]:
        """Get GeoJSON data for a specific layer."""
        return self.geojson_data.get(layer_id)

    async def get_available_layers(self) -> List[Dict[str, Any]]:
        """Get list of available historical map layers."""
        layers = []
        for layer_id, geojson in self.geojson_data.items():
            layers.append({
                "layer_id": layer_id,
                "name": layer_id.replace("-", " ").title(),
                "feature_count": len(geojson.get("features", []))
            })
        return layers
