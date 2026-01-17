"""
AI Synthesis Service - LLM-Powered Historical Reconstruction

Uses LLMs to synthesize historical data into coherent narratives.
Supports multiple providers: OpenAI, Anthropic.

CRITICAL GUIDELINES:
- Only use verified data from search results
- Never fabricate or embellish facts
- Clearly state when information is unavailable
- Cite sources for all claims
"""

import logging
import os
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)


class AISynthesisService:
    """Service for AI-powered historical synthesis."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Synthesis guidelines
        self.system_prompt = """You are a historical research assistant analyzing property records for Long Island, New York.

Your role is to synthesize available data into accurate historical narratives.

CRITICAL RULES:
1. ONLY use information from the provided records - NEVER fabricate facts
2. ALWAYS cite sources for every factual claim using [Source: name] format
3. CLEARLY state when information is missing or uncertain
4. Use phrases like "records indicate" or "according to [source]"
5. If no relevant records exist, say "No historical records found" - do NOT make up history
6. Distinguish clearly between documented facts and reasonable inferences
7. Note any contradictions between sources
8. Be precise about dates - don't guess if unsure

FORMAT:
- Write in clear, professional prose
- Include dates whenever available
- Organize chronologically
- Identify gaps in the historical record
- Be concise but thorough

Remember: It is better to say "no information found" than to fabricate history."""

    async def generate_comprehensive_report(
        self,
        address: str,
        lat: float,
        lon: float,
        parcel_data: Optional[dict],
        historical_records: List[dict],
        historical_events: List[dict],
        imagery_available: List[dict],
        deed_history: Optional[List[dict]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive AI-synthesized property history report.
        """
        # Build context for LLM
        context = self._build_context(
            address=address,
            lat=lat,
            lon=lon,
            parcel_data=parcel_data,
            historical_records=historical_records,
            historical_events=historical_events,
            imagery_available=imagery_available,
            deed_history=deed_history
        )

        # Generate synthesis
        if self.openai_api_key or self.anthropic_api_key:
            synthesis = await self._generate_with_llm(context)
        else:
            # Fallback to template-based synthesis
            synthesis = self._generate_template_synthesis(context)

        return synthesis

    def _build_context(
        self,
        address: str,
        lat: float,
        lon: float,
        parcel_data: Optional[dict],
        historical_records: List[dict],
        historical_events: List[dict],
        imagery_available: List[dict],
        deed_history: Optional[List[dict]]
    ) -> dict:
        """Build context object for synthesis."""
        return {
            "property": {
                "address": address,
                "coordinates": {"lat": lat, "lon": lon}
            },
            "parcel": parcel_data or {},
            "records": historical_records,
            "events": historical_events,
            "imagery": imagery_available,
            "deeds": deed_history or [],
            "record_count": len(historical_records),
            "event_count": len(historical_events)
        }

    async def _generate_with_llm(self, context: dict) -> Dict[str, Any]:
        """Generate synthesis using LLM."""
        try:
            if self.openai_api_key:
                return await self._synthesize_openai(context)
            elif self.anthropic_api_key:
                return await self._synthesize_anthropic(context)
        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")

        # Fallback
        return self._generate_template_synthesis(context)

    async def _synthesize_openai(self, context: dict) -> Dict[str, Any]:
        """Use OpenAI for synthesis."""
        import openai

        client = openai.AsyncOpenAI(api_key=self.openai_api_key)

        prompt = self._build_synthesis_prompt(context)

        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for factual accuracy
            max_tokens=4000
        )

        synthesis_text = response.choices[0].message.content

        return self._parse_synthesis_response(synthesis_text, context)

    async def _synthesize_anthropic(self, context: dict) -> Dict[str, Any]:
        """Use Anthropic for synthesis."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)

        prompt = self._build_synthesis_prompt(context)

        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        synthesis_text = response.content[0].text

        return self._parse_synthesis_response(synthesis_text, context)

    def _build_synthesis_prompt(self, context: dict) -> str:
        """Build the synthesis prompt."""
        prompt = f"""Please synthesize a historical report for the following Long Island property:

ADDRESS: {context['property']['address']}
COORDINATES: {context['property']['coordinates']['lat']}, {context['property']['coordinates']['lon']}

"""
        if context.get('parcel'):
            prompt += f"""PARCEL DATA:
{json.dumps(context['parcel'], indent=2)}

"""

        if context.get('records'):
            prompt += """HISTORICAL RECORDS FOUND:
"""
            for i, record in enumerate(context['records'][:20], 1):  # Limit to 20 records
                prompt += f"""
Record {i}:
- Source: {record.get('source_name', 'Unknown')}
- Date: {record.get('date', 'Unknown')}
- Snippet: {record.get('snippet', 'No text available')[:500]}
"""

        if context.get('events'):
            prompt += """
HISTORICAL EVENTS AFFECTING THIS AREA:
"""
            for event in context['events'][:10]:  # Limit to 10 events
                prompt += f"""
- {event.get('name', 'Unknown')} ({event.get('year', 'Unknown')})
  {event.get('description', '')[:200]}
"""

        if context.get('deeds'):
            prompt += """
DEED HISTORY:
"""
            for deed in context['deeds'][:10]:
                prompt += f"- {deed}\n"

        prompt += """
Please provide:
1. An executive summary (2-3 sentences)
2. A confidence level (high/medium/low/insufficient_data) with explanation
3. Key findings (bullet points)
4. Historical context for this area
5. Notable events that affected this property
6. Land use history (what the land was used for over time)
7. Identified gaps in the historical record
8. Recommendations for further research

Remember: Only cite facts from the provided data. If information is missing, say so clearly."""

        return prompt

    def _parse_synthesis_response(self, text: str, context: dict) -> Dict[str, Any]:
        """Parse LLM response into structured report."""
        # Extract sections from response
        report = {
            "property_address": context['property']['address'],
            "coordinates": context['property']['coordinates'],
            "executive_summary": self._extract_section(text, "executive summary", "summary"),
            "confidence_level": self._determine_confidence(text, context),
            "timeline": self._build_timeline_from_context(context),
            "key_findings": self._extract_list(text, "key findings", "findings"),
            "historical_context": self._extract_section(text, "historical context", "context"),
            "notable_events": self._format_events(context.get('events', [])),
            "land_use_history": self._extract_section(text, "land use", "use history"),
            "sources_cited": self._extract_sources(context),
            "data_gaps": self._extract_list(text, "gaps", "missing"),
            "recommendations_for_further_research": self._extract_list(text, "recommend", "further research"),
            "disclaimer": self._get_disclaimer()
        }

        return report

    def _generate_template_synthesis(self, context: dict) -> Dict[str, Any]:
        """Generate synthesis using templates (no LLM)."""
        address = context['property']['address']
        records = context.get('records', [])
        events = context.get('events', [])

        # Determine confidence
        if len(records) >= 5:
            confidence = "medium"
            confidence_note = "Multiple historical records found"
        elif len(records) >= 1:
            confidence = "low"
            confidence_note = "Limited historical records found"
        else:
            confidence = "insufficient_data"
            confidence_note = "No historical records found in digital archives"

        # Build summary
        if records:
            earliest = min(r.get('year', 9999) for r in records if r.get('year'))
            summary = (
                f"Historical records for {address} date back to {earliest}. "
                f"{len(records)} record(s) found in newspaper archives. "
            )
            if events:
                summary += f"This area was affected by {len(events)} significant historical events."
        else:
            summary = (
                f"No digitized historical records were found for {address} in the searched archives. "
                f"This does not mean no history exists - physical records may be available at county offices."
            )

        # Build findings
        findings = []
        if records:
            sources = set(r.get('source_name', 'Unknown') for r in records)
            findings.append(f"Found mentions in {len(sources)} newspaper source(s)")

            years = [r.get('year') for r in records if r.get('year')]
            if years:
                findings.append(f"Records span from {min(years)} to {max(years)}")

        for event in events[:3]:
            findings.append(f"Area affected by: {event.get('name', 'Unknown event')} ({event.get('year', '')})")

        if not findings:
            findings.append("No specific historical records found in digital archives")

        return {
            "property_address": address,
            "coordinates": context['property']['coordinates'],
            "executive_summary": summary,
            "confidence_level": confidence,
            "timeline": self._build_timeline_from_context(context),
            "key_findings": findings,
            "historical_context": self._generate_context_template(context),
            "notable_events": self._format_events(events),
            "land_use_history": "Unable to determine - insufficient historical records.",
            "sources_cited": self._extract_sources(context),
            "data_gaps": [
                "Pre-digital deed records (before ~1980)",
                "Local newspaper archives not fully digitized",
                "County clerk physical records",
                "Local historical society materials"
            ],
            "recommendations_for_further_research": [
                "Visit Suffolk/Nassau County Clerk's office for physical deed records",
                "Check local historical society archives",
                "Search FultonHistory.com manually for local newspapers",
                "Review fire insurance maps at Library of Congress",
                "Contact local library for microfilm newspaper archives"
            ],
            "disclaimer": self._get_disclaimer()
        }

    def _generate_context_template(self, context: dict) -> str:
        """Generate historical context from events."""
        events = context.get('events', [])

        if not events:
            return "Unable to establish specific historical context due to limited records."

        context_parts = []
        for event in events[:5]:
            context_parts.append(
                f"In {event.get('year', 'unknown year')}, this area was affected by {event.get('name', 'an event')}: "
                f"{event.get('description', '')[:200]}"
            )

        return " ".join(context_parts)

    def _build_timeline_from_context(self, context: dict) -> List[dict]:
        """Build timeline from records and events."""
        timeline = []

        for record in context.get('records', []):
            if record.get('date') and record.get('year'):
                timeline.append({
                    "date": record['date'],
                    "year": record['year'],
                    "event": f"Mentioned in {record.get('source_name', 'newspaper')}",
                    "source": record.get('source', ''),
                    "type": "mention"
                })

        for event in context.get('events', []):
            timeline.append({
                "date": event.get('date', ''),
                "year": event.get('year', 0),
                "event": event.get('name', ''),
                "source": "Historical Events Database",
                "type": event.get('event_type', 'event')
            })

        # Sort by year
        timeline.sort(key=lambda x: x.get('year', 0))

        return timeline

    def _format_events(self, events: List[dict]) -> List[dict]:
        """Format events for report."""
        return [
            {
                "name": e.get('name', ''),
                "date": e.get('date', ''),
                "description": e.get('description', ''),
                "type": e.get('event_type', ''),
                "relevance": e.get('relevance_to_property', '')
            }
            for e in events
        ]

    def _extract_sources(self, context: dict) -> List[str]:
        """Extract all sources cited."""
        sources = set()

        for record in context.get('records', []):
            source = record.get('source_name') or record.get('source', '')
            if source:
                sources.add(source)

        for event in context.get('events', []):
            for source in event.get('sources', []):
                sources.add(source)

        return list(sources)

    def _extract_section(self, text: str, *keywords) -> str:
        """Extract a section from text by keywords."""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Try to extract the section
                idx = text_lower.find(keyword.lower())
                # Get text after keyword until next section or end
                section = text[idx:idx + 500]
                return section.split('\n\n')[0].strip()
        return ""

    def _extract_list(self, text: str, *keywords) -> List[str]:
        """Extract a list from text by keywords."""
        items = []
        # Simple extraction - look for bullet points
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                items.append(line.lstrip('-•* ').strip())
        return items[:10]  # Limit to 10 items

    def _determine_confidence(self, text: str, context: dict) -> str:
        """Determine confidence level."""
        records = context.get('records', [])

        if "high" in text.lower() and len(records) >= 10:
            return "high"
        elif len(records) >= 3:
            return "medium"
        elif len(records) >= 1:
            return "low"
        else:
            return "insufficient_data"

    def _get_disclaimer(self) -> str:
        """Get standard disclaimer."""
        return (
            "This report is based only on digitally available records. "
            "Significant historical information may exist in physical archives "
            "that have not been digitized. This analysis does not constitute "
            "a professional title search or historical survey."
        )

    async def generate_quick_summary(
        self,
        address: str,
        lat: float,
        lon: float,
        records: List[dict]
    ) -> Dict[str, Any]:
        """Generate a quick one-line summary."""
        if not records:
            return {
                "address": address,
                "one_line_summary": "No historical records found in digital archives",
                "key_date": None,
                "key_fact": None,
                "historical_significance": "unknown",
                "sources": []
            }

        # Find earliest record
        earliest = min(records, key=lambda x: x.get('year', 9999))

        return {
            "address": address,
            "one_line_summary": f"Historical records date back to {earliest.get('year', 'unknown')}",
            "key_date": earliest.get('date'),
            "key_fact": earliest.get('snippet', '')[:100],
            "historical_significance": "medium" if len(records) > 5 else "low",
            "sources": list(set(r.get('source_name', '') for r in records))[:3]
        }

    async def generate_timeline(
        self,
        address: str,
        records: List[dict],
        events: List[dict],
        deed_history: Optional[List[dict]]
    ) -> List[dict]:
        """Generate a chronological timeline."""
        context = {
            'property': {'address': address},
            'records': records,
            'events': events,
            'deeds': deed_history or []
        }
        return self._build_timeline_from_context(context)

    async def fact_check(
        self,
        claim: str,
        address: str,
        records: List[dict]
    ) -> Dict[str, Any]:
        """Fact-check a historical claim."""
        # Simple fact-checking by searching records
        claim_lower = claim.lower()

        evidence = []
        contradictions = []

        for record in records:
            snippet = record.get('snippet', '').lower()

            # Look for supporting evidence
            words = claim_lower.split()
            matches = sum(1 for word in words if len(word) > 3 and word in snippet)

            if matches >= 2:
                evidence.append({
                    "source": record.get('source_name', ''),
                    "date": record.get('date', ''),
                    "text": record.get('snippet', '')[:200]
                })

        verified = len(evidence) > 0
        confidence = min(len(evidence) / 3, 1.0) if evidence else 0.0

        return {
            "verified": verified,
            "confidence": confidence,
            "evidence": evidence,
            "contradictions": contradictions,
            "notes": f"Found {len(evidence)} supporting record(s)" if evidence else "No supporting records found"
        }
