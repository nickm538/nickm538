# API Reference

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication. Rate limiting is applied to prevent abuse.

---

## Parcels API

### Search by Address

```http
GET /parcels/search/address
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Street address to search |
| include_boundary | boolean | No | Include parcel boundary polygon (default: true) |

**Response:**

```json
{
  "success": true,
  "message": "Found 1 parcel(s)",
  "results": [
    {
      "sbl": "0200-001.00-01.00-001.000",
      "address": "123 Main Street, Bay Shore",
      "municipality": "Islip",
      "county": "Suffolk",
      "owner_name": "John Doe",
      "acreage": 0.25,
      "land_use_code": "210",
      "land_use_description": "One Family Year-Round Residence",
      "year_built": 1955,
      "assessed_value": 450000,
      "deed_book": "12345",
      "deed_page": "123",
      "boundary": { "type": "Feature", "geometry": {...} },
      "centroid": { "lat": 40.7251, "lon": -73.2454 }
    }
  ],
  "total_count": 1
}
```

### Search by Coordinates

```http
GET /parcels/search/coordinates
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |
| include_boundary | boolean | No | Include parcel boundary (default: true) |

### Search by SBL

```http
GET /parcels/search/sbl/{sbl}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| sbl | string | Yes | Section-Block-Lot number |

---

## Imagery API

### Get Available Imagery

```http
GET /imagery/available
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |

**Response:**

```json
{
  "lat": 40.7251,
  "lon": -73.2454,
  "available_imagery": [
    {
      "layer_id": "nys_ortho_2022",
      "name": "NYS Orthoimagery 2022",
      "description": "2022 statewide 6-inch resolution",
      "year": 2022,
      "resolution": "6-inch",
      "source": "NYS GIS Program Office",
      "wms_url": "https://orthos.its.ny.gov/...",
      "tile_url": "https://orthos.its.ny.gov/.../tile/{z}/{y}/{x}"
    }
  ]
}
```

### Get Current Aerial

```http
GET /imagery/current
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |
| width | int | No | Image width (default: 1000) |
| height | int | No | Image height (default: 1000) |
| zoom_meters | float | No | View extent in meters (default: 200) |

### Get Historical Aerial

```http
GET /imagery/historical/{year}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year | int | Yes | Target year (1994-present) |
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |

### Get Tile Layer URLs

```http
GET /imagery/tile-urls
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| layer | string | Yes | Layer identifier |

---

## Historical Research API

### Deep Search

```http
POST /history/deep-search
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Property address |
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |
| year_start | int | No | Start year (default: 1700) |
| year_end | int | No | End year (default: 2000) |
| include_newspapers | boolean | No | Search newspapers (default: true) |
| include_military | boolean | No | Include military records (default: true) |
| include_deeds | boolean | No | Include deed records (default: true) |
| deep_mode | boolean | No | Exhaustive search (default: true) |

**Response:**

```json
{
  "success": true,
  "query_location": {
    "address": "123 Main Street, Bay Shore, NY",
    "lat": 40.7251,
    "lon": -73.2454
  },
  "total_records_found": 15,
  "records": [
    {
      "id": "loc_12345",
      "source": "chronicling_america",
      "source_name": "The Suffolk County News",
      "date": "1925-03-15",
      "year": 1925,
      "snippet": "The property at Main Street was sold...",
      "full_text_available": true,
      "url": "https://chroniclingamerica.loc.gov/...",
      "confidence_score": 0.85,
      "relevance_score": 0.75,
      "record_type": "newspaper"
    }
  ],
  "related_events": [
    {
      "event_id": "hurricane_1938",
      "name": "Great Hurricane of 1938",
      "date": "1938-09-21",
      "year": 1938,
      "description": "Category 3 hurricane struck Long Island...",
      "event_type": "natural_disaster"
    }
  ],
  "sources_searched": [
    "Library of Congress Chronicling America",
    "FultonHistory"
  ]
}
```

### Search Newspapers Directly

```http
GET /history/newspapers/search
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Search query |
| location | string | No | City or town name |
| year_start | int | No | Start year (default: 1800) |
| year_end | int | No | End year (default: 1960) |
| source | string | No | "loc", "fulton", or "all" (default: "all") |
| max_results | int | No | Maximum results (default: 50) |

### Get Long Island Events

```http
GET /history/events/long-island
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year_start | int | No | Start year (default: 1600) |
| year_end | int | No | End year (default: 2024) |
| event_type | string | No | Filter by event type |
| municipality | string | No | Filter by municipality |

### Get War History

```http
GET /history/events/wars
```

Returns comprehensive military history of Long Island.

---

## AI Synthesis API

### Generate Comprehensive Report

```http
POST /synthesis/comprehensive-report
```

**Request Body:**

```json
{
  "address": "123 Main Street, Bay Shore, NY",
  "lat": 40.7251,
  "lon": -73.2454,
  "parcel_data": { ... },
  "historical_records": [ ... ],
  "historical_events": [ ... ],
  "imagery_available": [ ... ],
  "synthesis_type": "comprehensive"
}
```

**Response:**

```json
{
  "property_address": "123 Main Street, Bay Shore, NY",
  "coordinates": { "lat": 40.7251, "lon": -73.2454 },
  "executive_summary": "Historical records for this property date back to 1925...",
  "confidence_level": "medium",
  "timeline": [
    {
      "date": "1925-03-15",
      "year": 1925,
      "event": "Property mentioned in Suffolk County News",
      "source": "Library of Congress"
    }
  ],
  "key_findings": [
    "Found 15 newspaper mentions between 1925-1960",
    "Area affected by 1938 hurricane"
  ],
  "historical_context": "Bay Shore developed as a resort community...",
  "notable_events": [ ... ],
  "land_use_history": "Originally farmland, developed for residential use...",
  "sources_cited": ["Library of Congress", "FultonHistory"],
  "data_gaps": ["Pre-1920 records not found"],
  "recommendations_for_further_research": [
    "Visit Suffolk County Clerk for physical deed records"
  ],
  "disclaimer": "This report is based only on digitally available records..."
}
```

### Generate Quick Summary

```http
POST /synthesis/quick-summary
```

### Fact Check Claim

```http
POST /synthesis/fact-check
```

---

## Maps API

### Get Available Sanborn Maps

```http
GET /maps/sanborn/available
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| lat | float | Yes | Latitude |
| lon | float | Yes | Longitude |
| municipality | string | No | City or town name |

### Get Historical Periods

```http
GET /maps/historical-periods
```

Returns list of historical time periods with associated map layers.

### Get GeoJSON Layer

```http
GET /maps/geojson/{layer_id}
```

| Layer ID | Description |
|----------|-------------|
| native-territories | Pre-contact Native American territories |
| dutch-settlements | Dutch colonial settlements |
| colonial-towns | Colonial township boundaries |
| battle-long-island | Revolutionary War battle sites |
| lirr-1890 | 1890 railroad network |
| military-ww2 | WWII military installations |
| levittown | Original Levittown boundaries |

### Get Native Territories

```http
GET /maps/native-territories
```

Returns GeoJSON for historical Native American territories.

### Get Tile Layers

```http
GET /maps/tile-layers
```

Returns XYZ tile layer configurations for map integration.

---

## Error Responses

All endpoints may return errors in this format:

```json
{
  "detail": "Error message describing the problem"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

---

## Rate Limiting

- 100 requests per minute per IP
- Deep search endpoints: 10 requests per minute

---

## Caching

- Parcel data: 24 hours
- Imagery: 7 days
- Historical records: 24 hours
- Geocoding: 30 days
