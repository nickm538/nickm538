"""
AI Synthesis API - LLM-Powered History Reconstruction

This module uses LLMs to synthesize historical data into coherent narratives.
It follows strict guidelines:
- Only use verified data from the search results
- Never fabricate or embellish historical facts
- Clearly state when information is unavailable
- Cite sources for all claims
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import os

from services.ai_synthesis_service import AISynthesisService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
synthesis_service = AISynthesisService()


class SynthesisRequest(BaseModel):
    """Request for AI synthesis of historical data."""
    address: str
    lat: float
    lon: float
    parcel_data: Optional[dict] = None
    historical_records: List[dict] = []
    historical_events: List[dict] = []
    imagery_available: List[dict] = []
    deed_history: Optional[List[dict]] = None
    synthesis_type: str = "comprehensive"  # comprehensive, timeline, narrative


class PropertyHistoryReport(BaseModel):
    """Comprehensive AI-synthesized property history report."""
    property_address: str
    coordinates: dict
    executive_summary: str
    confidence_level: str  # high, medium, low, insufficient_data
    timeline: List[dict]
    key_findings: List[str]
    historical_context: str
    notable_events: List[dict]
    ownership_history: Optional[str] = None
    land_use_history: str
    sources_cited: List[str]
    data_gaps: List[str]
    recommendations_for_further_research: List[str]
    disclaimer: str


class QuickSummary(BaseModel):
    """Brief AI-generated summary of property history."""
    address: str
    one_line_summary: str
    key_date: Optional[str] = None
    key_fact: Optional[str] = None
    historical_significance: str  # high, medium, low, unknown
    sources: List[str]


@router.post("/comprehensive-report")
async def generate_comprehensive_report(
    request: SynthesisRequest
) -> PropertyHistoryReport:
    """
    Generate a comprehensive AI-synthesized property history report.

    This uses an LLM to analyze all available data and create a coherent
    historical narrative. The AI is instructed to:

    1. Only use facts from the provided data
    2. Never fabricate or embellish
    3. Clearly state what is unknown
    4. Cite sources for all claims
    5. Identify gaps in the historical record

    The report includes:
    - Executive summary
    - Chronological timeline
    - Historical context
    - Notable events
    - Land use changes
    - Research recommendations
    """
    try:
        if not request.historical_records and not request.historical_events:
            # No data to synthesize
            return PropertyHistoryReport(
                property_address=request.address,
                coordinates={"lat": request.lat, "lon": request.lon},
                executive_summary="Insufficient historical data found for this property. "
                                  "No records were located in our searched archives.",
                confidence_level="insufficient_data",
                timeline=[],
                key_findings=[
                    "No historical newspaper mentions found",
                    "No deed records located in digital archives"
                ],
                historical_context="Unable to establish historical context due to lack of data.",
                notable_events=[],
                land_use_history="Unknown - no historical records found.",
                sources_cited=[],
                data_gaps=[
                    "Pre-digital deed records (before ~1980)",
                    "Local newspaper archives not yet digitized",
                    "County clerk physical records"
                ],
                recommendations_for_further_research=[
                    "Visit Suffolk/Nassau County Clerk's office for physical deed records",
                    "Check local historical society archives",
                    "Contact local library for microfilm newspaper archives",
                    "Review fire insurance maps at Library of Congress"
                ],
                disclaimer="This report is based only on digitally available records. "
                           "Significant historical information may exist in physical archives "
                           "that have not been digitized."
            )

        # Generate synthesis using AI
        report = await synthesis_service.generate_comprehensive_report(
            address=request.address,
            lat=request.lat,
            lon=request.lon,
            parcel_data=request.parcel_data,
            historical_records=request.historical_records,
            historical_events=request.historical_events,
            imagery_available=request.imagery_available,
            deed_history=request.deed_history
        )

        return PropertyHistoryReport(**report)

    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-summary")
async def generate_quick_summary(
    address: str = Query(...),
    lat: float = Query(...),
    lon: float = Query(...),
    records: List[dict] = []
) -> QuickSummary:
    """
    Generate a quick one-line summary of property history.

    Useful for map popups and search result previews.
    """
    try:
        summary = await synthesis_service.generate_quick_summary(
            address=address,
            lat=lat,
            lon=lon,
            records=records
        )
        return QuickSummary(**summary)
    except Exception as e:
        logger.error(f"Quick summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/timeline")
async def generate_timeline(
    request: SynthesisRequest
) -> dict:
    """
    Generate a chronological timeline of property history.

    Returns events sorted by date with source citations.
    """
    try:
        timeline = await synthesis_service.generate_timeline(
            address=request.address,
            records=request.historical_records,
            events=request.historical_events,
            deed_history=request.deed_history
        )

        return {
            "address": request.address,
            "timeline": timeline,
            "total_events": len(timeline),
            "earliest_date": timeline[0]["date"] if timeline else None,
            "latest_date": timeline[-1]["date"] if timeline else None
        }
    except Exception as e:
        logger.error(f"Timeline generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fact-check")
async def fact_check_claim(
    claim: str = Query(..., description="Historical claim to verify"),
    address: str = Query(..., description="Property address"),
    records: List[dict] = []
) -> dict:
    """
    Fact-check a historical claim against available records.

    Returns verification status and supporting evidence.
    """
    try:
        result = await synthesis_service.fact_check(
            claim=claim,
            address=address,
            records=records
        )

        return {
            "claim": claim,
            "verified": result["verified"],
            "confidence": result["confidence"],
            "supporting_evidence": result.get("evidence", []),
            "contradicting_evidence": result.get("contradictions", []),
            "notes": result.get("notes", "")
        }
    except Exception as e:
        logger.error(f"Fact check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis-prompts")
async def get_analysis_prompts():
    """
    Get the prompts used for AI analysis (for transparency).

    We believe in transparency about how AI is used in this system.
    """
    return {
        "synthesis_guidelines": """
            You are a historical research assistant analyzing property records
            for Long Island, New York. Your role is to synthesize available
            data into accurate historical narratives.

            CRITICAL RULES:
            1. ONLY use information from the provided records
            2. NEVER fabricate or embellish facts
            3. ALWAYS cite sources for claims
            4. CLEARLY state when information is missing or uncertain
            5. Use phrases like "records indicate" or "according to [source]"
            6. If no relevant records exist, say "No historical records found"
            7. Distinguish between facts and reasonable inferences
            8. Note any contradictions in sources

            FORMAT:
            - Write in clear, professional prose
            - Include dates whenever available
            - Note the source for each fact
            - Identify gaps in the historical record
        """,
        "confidence_levels": {
            "high": "Multiple corroborating sources",
            "medium": "Single reliable source or logical inference",
            "low": "Limited or unclear sources",
            "insufficient_data": "No relevant records found"
        }
    }
