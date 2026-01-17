# Long Island Historical Land Information System

A comprehensive research platform for discovering the deep historical connections of parcels of land on Long Island, New York.

![Long Island History](https://img.shields.io/badge/Coverage-Long%20Island%20NY-blue)
![Python](https://img.shields.io/badge/Backend-Python%20FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React%20TypeScript-blue)

## Overview

This system connects **Government Data** → **Historical Archives** → **AI Synthesis** to provide accurate, documented historical research for any Long Island property.

### Key Features

- **Interactive Map Interface**: Leaflet-based map with address/parcel search
- **NYS GIS Aerial Imagery**: Access orthoimagery from 1994-present
- **USGS Historical Maps**: Topographic maps dating back to the 1890s
- **Deep Historical Search**:
  - Library of Congress Chronicling America (50M+ newspaper pages)
  - FultonHistory (50M+ NY newspaper pages)
  - Local historical events database
- **AI-Powered Synthesis**: LLM-generated historical narratives with strict source citation
- **Sanborn Fire Insurance Maps**: Building history overlays
- **Historical Basemap Overlays**: Territorial maps from 100 BC to present

### Coverage Area

- Suffolk County
- Nassau County
- Historical Queens County territory
- Historical Kings County (Brooklyn) territory

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Map View │  │ Search   │  │ History  │  │ Report   │        │
│  │ (Leaflet)│  │ Panel    │  │ Panel    │  │ View     │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Layer                              │   │
│  │  /parcels  /imagery  /history  /synthesis  /maps         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Service Layer                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ Parcel      │ │ Imagery     │ │ Historical  │        │   │
│  │  │ Service     │ │ Service     │ │ Search      │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │ AI Synthesis│ │ Sanborn     │ │ Basemap     │        │   │
│  │  │ Service     │ │ Service     │ │ Service     │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ NYS GIS     │ │ Library of  │ │ FultonHistory│               │
│  │ Clearinghouse│ │ Congress    │ │ (Scraper)   │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ Suffolk     │ │ Nassau      │ │ USGS        │               │
│  │ County GIS  │ │ County GIS  │ │ National Map│               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd long_island_history/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Start the backend server
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd long_island_history/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/parcels/search/address` | Search parcels by address |
| `GET /api/parcels/search/coordinates` | Search parcels by lat/lon |
| `GET /api/imagery/available` | Get available aerial imagery |
| `GET /api/imagery/historical/{year}` | Get historical aerial |
| `POST /api/history/deep-search` | Deep historical archive search |
| `POST /api/synthesis/comprehensive-report` | Generate AI report |
| `GET /api/maps/sanborn/available` | Get Sanborn fire maps |
| `GET /api/maps/historical-periods` | Get historical map layers |

## Data Sources

### Imagery Sources

| Source | Coverage | Years |
|--------|----------|-------|
| NYS GIS Orthoimagery | Statewide | 1994-Present |
| USGS Historical Topo | National | 1880s-Present |
| USGS Aerial | National | Various |

### Historical Archives

| Source | Content | Coverage |
|--------|---------|----------|
| Chronicling America | Historical newspapers | 1789-1963 |
| FultonHistory | NY newspapers | 1795-2007 |
| Sanborn Maps | Fire insurance maps | 1867-1970 |

### Parcel Data

| Source | Data |
|--------|------|
| Suffolk County GIS | Parcel boundaries, SBL, ownership |
| Nassau County GIS | Parcel boundaries, SBL, ownership |

## Configuration

### Environment Variables

```bash
# API Keys (optional - enables AI synthesis)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database (optional)
DATABASE_URL=sqlite:///./li_history.db

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
```

## Historical Periods Covered

- **Pre-Contact Era** (Before 1624): Metoac, Shinnecock, Montaukett territories
- **Dutch Colonial** (1624-1664): First European settlements
- **English Colonial** (1664-1776): Township establishment
- **Revolutionary War** (1776-1783): Battle of Long Island, British occupation
- **Early Republic** (1783-1860): Agricultural economy, railroad
- **Gilded Age** (1865-1900): Gold Coast estates
- **World Wars** (1914-1945): Aviation industry, military bases
- **Post-War** (1945-1970): Levittown, suburbanization
- **Modern Era** (1970-Present): Contemporary development

## Important Notes

### Accuracy Commitment

This system follows strict accuracy guidelines:
- **Only verified sources** are used
- **No fabrication** of historical facts
- **Clear disclosure** when information is unavailable
- **Source citation** for all claims

### Limitations

- Pre-digital records (before ~1980) may not be fully available online
- Some local newspapers are not yet digitized
- Physical deed records at county offices may contain additional information
- This is not a substitute for professional title searches

## Project Structure

```
long_island_history/
├── backend/
│   ├── api/                 # API route handlers
│   │   ├── parcels.py       # Parcel data endpoints
│   │   ├── imagery.py       # Imagery endpoints
│   │   ├── history.py       # Historical search endpoints
│   │   ├── synthesis.py     # AI synthesis endpoints
│   │   └── maps.py          # Map layer endpoints
│   ├── services/            # Business logic services
│   │   ├── parcel_service.py
│   │   ├── imagery_service.py
│   │   ├── chronicling_america_service.py
│   │   ├── fulton_history_service.py
│   │   ├── ai_synthesis_service.py
│   │   └── ...
│   ├── utils/               # Utility modules
│   ├── main.py              # Application entry point
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   ├── store/           # Zustand state management
│   │   └── styles/          # CSS styles
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Additional documentation
└── README.md
```

## Contributing

Contributions are welcome! Please ensure any changes maintain the accuracy-first approach of this system.

## License

This project is provided for educational and research purposes.

## Acknowledgments

- NYS GIS Program Office
- Library of Congress
- FultonHistory.com
- USGS National Map
- Suffolk County Government
- Nassau County Government
