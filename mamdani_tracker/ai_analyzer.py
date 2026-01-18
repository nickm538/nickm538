"""
AI-Powered Promise Analyzer using Google Gemini API
Provides intelligent, nuanced analysis with frank human perspective

Not just tracking what's technically done - evaluating actual outcomes,
connecting policies to real-world effects, and minimizing bias through
comprehensive multi-perspective analysis.
"""
import os
from google import genai
from google.genai import types
from datetime import datetime
from typing import List, Dict, Optional
import json


class GeminiPromiseAnalyzer:
    """
    Uses Google Gemini for intelligent, nuanced analysis of:
    - Whether news actually indicates real progress (not just announcements)
    - Real-world impact vs. paper accomplishments
    - Detecting stance changes and pragmatic adjustments
    - Providing balanced multi-perspective views
    """

    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    def _make_request(self, prompt: str, system_instruction: str = None, 
                      temperature: float = 0.3) -> Optional[str]:
        """Make a request to Gemini API with error handling"""
        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=4000,
            )
            
            if system_instruction:
                config.system_instruction = system_instruction
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response text, handling markdown code blocks"""
        if not text:
            return None
        
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    return None
        return None

    def analyze_news_for_promise(self, news_content: str, news_source: str,
                                  promise_title: str, promise_description: str,
                                  current_status: str) -> Dict:
        """
        Analyze news with nuanced, real-world perspective.
        Not just "is this relevant" but "what does this actually mean."
        """
        system_instruction = """You're a veteran NYC political analyst who's seen it all.
        You know the difference between a press release and actual progress, between 
        an announcement and implementation, between political theater and real change.
        
        Your job is to cut through the noise and give the honest assessment:
        - Is this actually meaningful or just optics?
        - What would this mean for real New Yorkers if it happens?
        - What are the chances it actually gets implemented?
        - Is this a real step forward, a symbolic gesture, or spin?
        
        Be frank but fair. Don't be cynical for cynicism's sake, but don't be naive either.
        Politicians announce things all the time - what matters is what actually happens.
        
        Always respond with valid JSON only."""

        prompt = f"""Analyze this news about Mayor Mamdani and give me the real assessment:

NEWS SOURCE: {news_source}
NEWS CONTENT:
{news_content}

CAMPAIGN PROMISE BEING TRACKED:
Title: {promise_title}
Description: {promise_description}
Current Status: {current_status}

Give me the honest analysis in this JSON format:
{{
    "is_relevant": true or false,
    "relevance_score": 0.0 to 1.0,
    "relevance_reasoning": "Why this matters (or doesn't) for this promise",
    
    "substance_assessment": "Real Progress" or "Symbolic/Optics" or "Just Announcement" or "Mixed" or "Not Applicable",
    "substance_explanation": "What's actually happening vs what's being claimed",
    
    "indicates_status_change": true or false,
    "suggested_new_status": "Not Started" or "In Progress" or "Delivered" or "Partially Delivered" or "Stalled" or "Failed" or "Walked Back" or null,
    "status_reasoning": "Evidence-based explanation of status",
    
    "real_world_impact": "What this actually means for New Yorkers - be specific",
    "implementation_likelihood": 0.0 to 1.0,
    "implementation_obstacles": "What could prevent this from actually happening",
    
    "stance_change_detected": true or false,
    "stance_change_type": "Reversal" or "Walkback" or "Pragmatic Adjustment" or "Rhetorical Shift" or "None",
    "stance_change_details": "Honest assessment of any evolution from campaign position",
    
    "sentiment": "Positive" or "Negative" or "Neutral" or "Mixed",
    "confidence": 0.0 to 1.0,
    
    "bias_in_source": "Left" or "Right" or "Center" or "Unknown",
    "bias_notes": "Any spin or framing to be aware of",
    
    "frank_assessment": "Your honest, conversational take on what this means - talk like a real person"
}}

Return ONLY the JSON, no other text."""

        result = self._make_request(prompt, system_instruction, temperature=0.4)
        analysis = self._extract_json(result)
        
        if analysis:
            analysis['timestamp'] = datetime.utcnow().isoformat()
            analysis['promise_title'] = promise_title
            analysis['success'] = True
            return analysis
        
        return {
            'success': False,
            'error': 'Failed to parse response',
            'raw_response': result
        }

    def batch_analyze_research_results(self, research_content: str, 
                                        promises: List[Dict]) -> Dict:
        """
        Analyze research results with nuanced, comprehensive perspective.
        """
        promise_list = "\n".join([
            f"{i+1}. [{p.get('category', 'Other')}] {p['title']} (Current: {p.get('status', 'Unknown')})"
            for i, p in enumerate(promises)
        ])

        system_instruction = """You're a seasoned political analyst who gives it to people straight.
        You've covered NYC politics for years and you know how to separate signal from noise.
        
        Your job is to analyze this research and tell people what's actually happening with
        each campaign promise - not the spin, not the attacks, just the honest assessment.
        
        For each promise, think about:
        - Is there real progress or just talk?
        - What would success actually look like and are we getting there?
        - What are the real obstacles?
        - Is the administration serious about this or is it back-burner?
        
        Be balanced but don't be wishy-washy. If something is working, say so. If it's not, say that too.
        
        Always respond with valid JSON only."""

        prompt = f"""Analyze this research against the campaign promises and give me the real story:

RESEARCH CONTENT:
{research_content}

CAMPAIGN PROMISES TO EVALUATE:
{promise_list}

For each promise that's mentioned or relevant, give me the honest assessment.
Return JSON in this format:
{{
    "analysis_timestamp": "ISO timestamp",
    "overall_assessment": "Your frank, conversational summary of how the administration is doing overall",
    
    "promises_analyzed": [
        {{
            "promise_number": 1,
            "promise_title": "title",
            "is_mentioned": true or false,
            "relevance_score": 0.0 to 1.0,
            
            "current_evidence": "What the research actually shows about this promise",
            "real_vs_announced": "What's actually happening vs what's been announced",
            
            "suggested_status": "Not Started" or "In Progress" or "Delivered" or "Partially Delivered" or "Stalled" or "Walked Back" or "No Change",
            "status_confidence": 0.0 to 1.0,
            "status_reasoning": "Why you're making this assessment",
            
            "implementation_reality": "Honest assessment of whether this is actually getting done",
            "key_obstacles": "What's standing in the way",
            
            "stance_change": true or false,
            "stance_change_type": "None" or "Reversal" or "Walkback" or "Pragmatic Adjustment",
            "stance_change_details": "Details if position has evolved",
            
            "frank_take": "Your honest, conversational assessment - what would you tell a friend who asked about this?"
        }}
    ],
    
    "biggest_wins": ["Promises where real progress is being made"],
    "biggest_concerns": ["Promises that seem stalled or walked back"],
    "things_to_watch": ["Developments that could be significant"],
    
    "notable_stance_changes": ["Any significant evolution from campaign positions"],
    "promises_not_mentioned": [list of promise numbers with no relevant news]
}}

Return ONLY the JSON, no other text."""

        result = self._make_request(prompt, system_instruction, temperature=0.4)
        analysis = self._extract_json(result)
        
        if analysis:
            analysis['success'] = True
            return analysis
        
        return {
            'success': False,
            'error': 'Failed to parse response',
            'raw_response': result
        }

    def generate_promise_update_summary(self, promise: Dict, 
                                         new_evidence: str,
                                         old_status: str,
                                         new_status: str) -> str:
        """
        Generate a frank, human-readable summary of a promise update.
        """
        system_instruction = """You're a straight-talking political reporter.
        Write like you're explaining this to a smart friend over coffee - clear, honest, no jargon.
        Don't be preachy or dramatic, just give people the real story in plain language."""

        prompt = f"""Write a brief, frank summary of this promise update:

PROMISE: {promise['title']}
CATEGORY: {promise.get('category', 'Other')}
OLD STATUS: {old_status}
NEW STATUS: {new_status}

WHAT HAPPENED:
{new_evidence}

Write 2-3 sentences that tell people what actually happened and what it means.
Be honest - if this is a big deal, say so. If it's mostly symbolic, say that too.
Talk like a real person, not a press release."""

        result = self._make_request(prompt, system_instruction, temperature=0.5)
        return result or "Status update recorded."

    def get_balanced_perspective(self, topic: str, context: str) -> Dict:
        """
        Get a balanced, multi-perspective view on a topic to minimize bias.
        """
        system_instruction = """You're committed to helping people understand all sides of an issue.
        You believe that even when you have a personal view, people deserve to hear the strongest
        version of arguments they might disagree with.
        
        Your job is to present multiple perspectives fairly and help people understand WHY
        reasonable people might see this differently.
        
        Don't do false balance - if the evidence clearly points one way, say so. But on genuinely
        contested issues, give voice to the range of legitimate views.
        
        Always respond with valid JSON only."""

        prompt = f"""Give me the full picture on this topic:

TOPIC: {topic}
CONTEXT: {context}

Present the range of perspectives in this JSON format:
{{
    "topic": "{topic}",
    
    "administration_view": {{
        "position": "What the Mamdani administration says/believes",
        "strongest_argument": "The best case for their position",
        "evidence_cited": "What they point to as support"
    }},
    
    "progressive_view": {{
        "position": "What progressive allies/critics say",
        "strongest_argument": "Their best case",
        "concerns": "What they're worried about"
    }},
    
    "moderate_view": {{
        "position": "What moderates/centrists say",
        "strongest_argument": "Their best case",
        "concerns": "Their main worries"
    }},
    
    "conservative_view": {{
        "position": "What conservatives/business interests say",
        "strongest_argument": "Their best case",
        "concerns": "Their main objections"
    }},
    
    "affected_communities": {{
        "who": "Who's most directly affected",
        "what_theyre_saying": "Their actual perspective (not what politicians claim)",
        "key_concerns": "What matters most to them"
    }},
    
    "expert_consensus": {{
        "what_experts_say": "Academic/professional expert view if available",
        "key_evidence": "What the data/research shows",
        "uncertainties": "What we don't know yet"
    }},
    
    "synthesis": {{
        "where_sides_agree": "Common ground if any",
        "core_disagreement": "What the fundamental dispute is about",
        "my_assessment": "Your honest take after considering all sides",
        "what_to_watch": "What would tell us who's right"
    }}
}}

Return ONLY the JSON, no other text."""

        result = self._make_request(prompt, system_instruction, temperature=0.4)
        analysis = self._extract_json(result)
        
        if analysis:
            analysis['success'] = True
            analysis['timestamp'] = datetime.utcnow().isoformat()
            return analysis
        
        return {
            'success': False,
            'error': 'Failed to parse response'
        }

    def compare_campaign_vs_current_position(self, promise_title: str,
                                              campaign_position: str,
                                              current_evidence: str) -> Dict:
        """
        Compare campaign promises to current reality with nuanced assessment.
        """
        system_instruction = """You're a political fact-checker who understands nuance.
        You know that some "flip-flops" are actually reasonable adjustments to governing reality,
        while others are genuine betrayals. Your job is to help people understand the difference.
        
        Be fair but honest. Politicians do have to adjust to reality once in office, but voters
        deserve to know when promises are being abandoned vs. adapted vs. genuinely pursued.
        
        Always respond with valid JSON only."""

        prompt = f"""Compare what was promised vs. what's happening:

PROMISE: {promise_title}

WHAT WAS PROMISED (Campaign):
{campaign_position}

WHAT'S ACTUALLY HAPPENING (Current):
{current_evidence}

Give me the honest comparison in this JSON format:
{{
    "promise_kept": "Yes" or "No" or "Partially" or "In Progress" or "Too Early" or "Walked Back",
    "consistency_score": 0.0 to 1.0,
    
    "what_was_promised": "Clear summary of the campaign commitment",
    "what_is_happening": "Clear summary of current reality",
    
    "the_gap": "Honest description of any difference between promise and reality",
    "gap_type": "None" or "Timing" or "Scale" or "Approach" or "Fundamental",
    
    "is_this_reasonable": true or false,
    "reasonableness_explanation": "Is the gap justified by real constraints, or is this a broken promise?",
    
    "fulfillment_evidence": ["Specific evidence of promise being kept"],
    "breaking_evidence": ["Specific evidence of promise being abandoned"],
    "adjustment_evidence": ["Evidence of pragmatic modifications"],
    
    "who_benefits": "Who wins if current approach continues",
    "who_loses": "Who loses compared to what was promised",
    
    "frank_assessment": "Your honest, conversational take - is this person keeping their word?",
    "confidence": 0.0 to 1.0
}}

Return ONLY the JSON, no other text."""

        result = self._make_request(prompt, system_instruction, temperature=0.4)
        analysis = self._extract_json(result)
        
        if analysis:
            analysis['timestamp'] = datetime.utcnow().isoformat()
            analysis['success'] = True
            return analysis
        
        return {
            'success': False,
            'error': 'Failed to parse response'
        }


# Alias for backward compatibility
OpenAIPromiseAnalyzer = GeminiPromiseAnalyzer
