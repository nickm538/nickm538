# Data Sources Documentation

This document details all external data sources used by the Long Island Historical Land Information System.

## 1. NYS GIS Clearinghouse

**Organization:** New York State GIS Program Office
**URL:** https://gis.ny.gov
**Data Type:** Orthoimagery (Aerial Photography)
**API Type:** WMS/WMTS (OGC Standards)

### Available Services

| Service | Years | Resolution | Description |
|---------|-------|------------|-------------|
| Latest | Current | 6-inch | Most recent statewide imagery |
| 2022 | 2022 | 6-inch | Statewide leaf-off |
| 2019 | 2019 | 1-foot | Statewide leaf-off |
| 2016 | 2016 | 1-foot | Statewide |
| 2013 | 2013 | 1-foot | Selected counties |
| 2010 | 2010 | 1-foot | Selected counties |
| 2008 | 2008 | 1-foot | Selected counties |
| 2004 | 2004 | 1-foot | Nassau/Suffolk |
| 2001 | 2001 | 2-foot | Long Island |
| 1994 | 1994 | 1-meter | First statewide digital |

### Endpoints

```
Base URL: https://orthos.its.ny.gov/arcgis/rest/services/wms
WMS: {base}/{year}/MapServer/WMSServer
Tiles: {base}/{year}/MapServer/tile/{z}/{y}/{x}
```

### Usage Notes

- "Leaf-off" imagery (taken in winter) shows ground and building foundations better
- Higher resolution for recent years
- Free, no authentication required
- Government-grade rectified imagery suitable for planning

---

## 2. Library of Congress - Chronicling America

**Organization:** Library of Congress
**URL:** https://chroniclingamerica.loc.gov
**Data Type:** Digitized Historical Newspapers
**API Type:** REST API (JSON)

### Coverage

- **Date Range:** 1777-1963
- **Total Pages:** 50+ million
- **New York Papers:** Hundreds of titles including major NYC papers

### API Endpoints

```
Search: https://chroniclingamerica.loc.gov/search/pages/results/
Newspaper Info: https://chroniclingamerica.loc.gov/lccn/{lccn}.json
Page OCR: https://chroniclingamerica.loc.gov/lccn/{lccn}/{date}/ed-{edition}/seq-{seq}/ocr.txt
```

### Search Parameters

| Parameter | Description |
|-----------|-------------|
| proxtext | Search query |
| state | State filter |
| date1 | Start year |
| date2 | End year |
| rows | Results per page |
| format | json |

### Long Island Newspapers Available

- The Sun (New York)
- New York Tribune
- Brooklyn Daily Eagle
- The Long-Islander
- Suffolk County News

---

## 3. FultonHistory (Old Fulton NY Post Cards)

**Organization:** Tom Tryniski (Private Archive)
**URL:** https://fultonhistory.com
**Data Type:** Digitized NY State Newspapers
**Access Method:** Web Scraping (No Public API)

### Coverage

- **Total Pages:** 50+ million
- **Date Range:** 1795-2007
- **Focus:** New York State newspapers

### Long Island Papers (Partial List)

- The Long-Islander (Huntington)
- Suffolk County News
- South Side Signal
- Babylon Signal
- Sag Harbor Express
- East Hampton Star
- Southampton Press
- Riverhead News
- Port Jefferson Echo
- Patchogue Advance
- Bay Shore Sentinel
- Islip Press
- Northport Journal
- Glen Cove Record-Pilot
- Nassau County Review
- Freeport Review
- Hempstead Sentinel
- Oyster Bay Guardian

### Usage Notes

- No public API - requires web scraping
- Respectful rate limiting required (2+ seconds between requests)
- Single largest repository of NY newspaper history
- Essential for Long Island research

---

## 4. Suffolk County GIS

**Organization:** Suffolk County Government
**URL:** https://gis.suffolkcountyny.gov
**Data Type:** Parcel Data, Property Records
**API Type:** ArcGIS REST API

### Available Data

- Parcel boundaries (polygons)
- Section-Block-Lot (SBL) numbers
- Property owner names
- Assessed values
- Deed book/page references
- Land use codes
- Building year built

### Endpoints

```
Parcels: https://gis.suffolkcountyny.gov/arcgis/rest/services/Parcels/FeatureServer/0
```

### Query Parameters

| Parameter | Description |
|-----------|-------------|
| geometry | Point or polygon |
| geometryType | esriGeometryPoint |
| spatialRel | esriSpatialRelIntersects |
| outFields | * (all fields) |
| returnGeometry | true/false |
| f | json |

---

## 5. Nassau County GIS

**Organization:** Nassau County Government
**URL:** https://www.nassaucountyny.gov/gis
**Data Type:** Parcel Data, Property Records
**API Type:** ArcGIS REST API

### Available Data

Similar to Suffolk County:
- Parcel boundaries
- SBL numbers
- Property information
- Assessment data

---

## 6. USGS National Map

**Organization:** U.S. Geological Survey
**URL:** https://www.usgs.gov/programs/national-geospatial-program/national-map
**Data Type:** Topographic Maps, Imagery
**API Type:** REST API, Tile Services

### Historical Topographic Maps

| Series | Scale | Years |
|--------|-------|-------|
| 15-minute | 1:62,500 | 1890s-1950s |
| 7.5-minute | 1:24,000 | 1947-present |

### Endpoints

```
Products API: https://tnmaccess.nationalmap.gov/api/v1/products
Topo Tiles: https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}
Imagery: https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}
```

### TopoView

Interactive viewer for historical maps:
```
https://ngmdb.usgs.gov/topoview/viewer/#{zoom}/{lat}/{lon}
```

---

## 7. Sanborn Fire Insurance Maps

**Organization:** Library of Congress / ProQuest
**URL:** https://www.loc.gov/collections/sanborn-maps
**Data Type:** Detailed Building Maps
**Access:** Free (LOC) / Subscription (ProQuest)

### Coverage for Long Island

| Location | Years Available |
|----------|-----------------|
| Bay Shore | 1893, 1898, 1904, 1910, 1921, 1930 |
| Huntington | 1886, 1893, 1898, 1910, 1921 |
| Patchogue | 1886, 1893, 1898, 1910, 1921 |
| Freeport | 1893, 1898, 1910, 1921, 1930 |
| Hempstead | 1886, 1893, 1898, 1910, 1921 |
| And many more... |

### Map Legend

| Color | Meaning |
|-------|---------|
| Pink | Brick construction |
| Yellow | Frame (wood) |
| Blue | Stone |
| Brown | Adobe/special |
| Green | Iron/steel |

### Usage Notes

- Library of Congress has free medium-resolution scans
- ProQuest (subscription) has high-resolution versions
- Many public libraries provide ProQuest access

---

## 8. US Census Bureau Geocoder

**Organization:** U.S. Census Bureau
**URL:** https://geocoding.geo.census.gov
**Data Type:** Address Geocoding
**API Type:** REST API

### Endpoint

```
https://geocoding.geo.census.gov/geocoder/locations/onelineaddress
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| address | Full address string |
| benchmark | Public_AR_Current |
| format | json |

---

## Data Quality Notes

### Verification Approach

All data is verified through multiple sources when possible:

1. **Cross-reference** newspaper mentions across multiple papers
2. **Validate** dates against known historical events
3. **Confirm** locations using period maps
4. **Check** official records (GIS, county clerk)

### Known Gaps

1. **Pre-1880s** - Limited digitized newspapers
2. **Pre-1980s deeds** - Physical records only
3. **Some local papers** - Not yet digitized
4. **Private archives** - Historical societies may have additional material

### Recommendation for Complete Research

For comprehensive property research, supplement this system with:

1. **County Clerk's Office** - Physical deed records
2. **Local Historical Societies** - Photos, maps, personal accounts
3. **Library Microfilm** - Additional newspaper archives
4. **State Archives** - Official records, patents

---

## API Rate Limits

| Source | Rate Limit | Notes |
|--------|------------|-------|
| Library of Congress | No official limit | Be respectful |
| NYS GIS | No limit | Government service |
| USGS | No limit | Government service |
| FultonHistory | N/A | 2+ sec between requests |
| County GIS | No official limit | Be respectful |

---

## Attribution Requirements

When using data from these sources, proper attribution is required:

- **NYS GIS:** "NYS GIS Program Office"
- **Library of Congress:** "Library of Congress, Chronicling America"
- **USGS:** "USGS National Map"
- **FultonHistory:** "FultonHistory.com"
