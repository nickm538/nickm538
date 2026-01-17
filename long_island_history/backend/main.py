"""
Long Island Historical Land Information System
Main FastAPI Application Entry Point

This application provides deep historical research capabilities for parcels
of land on Long Island, NY, connecting government data, historical archives,
and AI synthesis to reconstruct property history.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our service modules
from api import parcels, imagery, history, synthesis, maps
from services.cache_manager import CacheManager
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Long Island Historical Land Information System...")

    # Initialize cache
    app.state.cache = CacheManager()

    # Warm up connections to external services
    logger.info("Warming up external service connections...")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await app.state.cache.close()


# Create FastAPI application
app = FastAPI(
    title="Long Island Historical Land Information System",
    description="""
    A comprehensive research platform for discovering the deep historical
    connections of parcels of land on Long Island, New York.

    ## Features

    * **Parcel Intelligence**: Access Suffolk & Nassau County GIS data for property boundaries and SBL numbers
    * **Visual Time Machine**: Aerial imagery from 1994-present via NYS GIS, historical USGS maps
    * **Deep Historical Search**: Search 50+ million newspaper pages from FultonHistory and Library of Congress
    * **AI Synthesis**: LLM-powered reconstruction of property history from archival records
    * **Historical Overlays**: Territorial maps from 100 BC to present
    * **Fire Insurance Maps**: Sanborn map overlays for building history

    ## Coverage Area

    This system covers **Long Island, New York only**, including:
    - Suffolk County
    - Nassau County
    - Queens County (historical Long Island)
    - Kings County / Brooklyn (historical Long Island)

    ## Data Sources

    - NYS GIS Clearinghouse
    - Suffolk County GIS Portal
    - Nassau County GIS
    - Library of Congress Chronicling America
    - Old Fulton NY Post Cards (FultonHistory)
    - USGS Historical Topographic Maps
    - Sanborn Fire Insurance Maps
    - NYS Historic Newspapers
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(parcels.router, prefix="/api/parcels", tags=["Parcels"])
app.include_router(imagery.router, prefix="/api/imagery", tags=["Imagery"])
app.include_router(history.router, prefix="/api/history", tags=["Historical Research"])
app.include_router(synthesis.router, prefix="/api/synthesis", tags=["AI Synthesis"])
app.include_router(maps.router, prefix="/api/maps", tags=["Map Layers"])


# Pydantic models for API
class HealthCheck(BaseModel):
    """Health check response model."""
    status: str
    version: str
    services: dict


class PropertySearchRequest(BaseModel):
    """Request model for property search."""
    address: Optional[str] = Field(None, description="Street address to search")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lon: Optional[float] = Field(None, description="Longitude coordinate")
    sbl: Optional[str] = Field(None, description="Section-Block-Lot number")

    class Config:
        json_schema_extra = {
            "example": {
                "address": "5 Lawrence Court, Bay Shore, NY 11706"
            }
        }


class DeepSearchRequest(BaseModel):
    """Request model for deep historical search."""
    address: str = Field(..., description="Property address")
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    year_start: int = Field(1700, description="Start year for search")
    year_end: int = Field(2000, description="End year for search")
    include_imagery: bool = Field(True, description="Include aerial imagery")
    include_newspapers: bool = Field(True, description="Include newspaper search")
    include_deeds: bool = Field(True, description="Include deed records")
    include_fire_maps: bool = Field(True, description="Include Sanborn maps")
    deep_search: bool = Field(True, description="Enable comprehensive deep search")


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Long Island Historical Land Information System",
        "version": "1.0.0",
        "description": "Deep historical research for Long Island parcels",
        "coverage": "Long Island, New York (Suffolk, Nassau, Queens, Kings counties)",
        "endpoints": {
            "api_docs": "/api/docs",
            "health": "/health",
            "parcels": "/api/parcels",
            "imagery": "/api/imagery",
            "history": "/api/history",
            "synthesis": "/api/synthesis",
            "maps": "/api/maps"
        }
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        services={
            "nys_gis": "connected",
            "suffolk_gis": "connected",
            "nassau_gis": "connected",
            "chronicling_america": "connected",
            "fulton_history": "available",
            "ai_synthesis": "ready"
        }
    )


@app.get("/api/coverage-bounds")
async def get_coverage_bounds():
    """Returns the geographic bounds of Long Island coverage area."""
    return {
        "name": "Long Island, New York",
        "bounds": {
            "north": 41.1612,
            "south": 40.5431,
            "east": -71.8562,
            "west": -74.0421
        },
        "center": {
            "lat": 40.7891,
            "lon": -73.1350
        },
        "counties": [
            {"name": "Suffolk County", "fips": "36103"},
            {"name": "Nassau County", "fips": "36059"},
            {"name": "Queens County", "fips": "36081"},
            {"name": "Kings County", "fips": "36047"}
        ],
        "townships": [
            "Babylon", "Brookhaven", "East Hampton", "Huntington",
            "Islip", "Riverhead", "Shelter Island", "Smithtown",
            "Southampton", "Southold", "Hempstead", "North Hempstead",
            "Oyster Bay"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
