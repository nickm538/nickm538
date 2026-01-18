"""
Daily Research Engine for Mamdani Promise Tracker
Combines Perplexity Sonar (real-time news) + Gemini (intelligent analysis)
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
import json
import time

from ai_research import PerplexityResearcher
from ai_analyzer import GeminiPromiseAnalyzer


class DailyResearchEngine:
    """
    Orchestrates daily research workflow:
    1. Perplexity fetches real-time news and updates
    2. Gemini analyzes relevance to each promise
    3. Status changes are detected and logged
    4. Stance changes are tracked
    """

    def __init__(self):
        self.researcher = PerplexityResearcher()
        self.analyzer = GeminiPromiseAnalyzer()
        self.research_log = []

    def run_daily_research(self, promises: List[Dict]) -> Dict:
        """
        Run the complete daily research workflow.
        
        Args:
            promises: List of promise dicts with id, title, description, category, status
            
        Returns:
            Comprehensive research results with updates for each promise
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'research_date': datetime.now().strftime('%Y-%m-%d'),
            'daily_news': None,
            'stance_changes_research': None,
            'promise_updates': [],
            'status_changes': [],
            'stance_changes_detected': [],
            'errors': [],
            'summary': None
        }

        print(f"[{datetime.now()}] Starting daily research...")

        # Step 1: Get daily news overview from Perplexity
        print("Step 1: Fetching daily Mamdani news via Perplexity...")
        daily_news = self.researcher.get_daily_mamdani_news()
        results['daily_news'] = daily_news
        
        if not daily_news['success']:
            results['errors'].append(f"Daily news fetch failed: {daily_news.get('error')}")
            print(f"  ERROR: {daily_news.get('error')}")
        else:
            print(f"  SUCCESS: Retrieved daily news with {len(daily_news.get('citations', []))} citations")
        
        time.sleep(2)  # Rate limiting

        # Step 2: Check for stance changes from Perplexity
        print("Step 2: Checking for stance changes via Perplexity...")
        stance_research = self.researcher.detect_stance_changes()
        results['stance_changes_research'] = stance_research
        
        if not stance_research['success']:
            results['errors'].append(f"Stance change check failed: {stance_research.get('error')}")
            print(f"  ERROR: {stance_research.get('error')}")
        else:
            print(f"  SUCCESS: Stance change research complete")
        
        time.sleep(2)

        # Step 3: Batch analyze daily news against all promises using Gemini
        if daily_news['success'] and daily_news.get('content'):
            print("Step 3: Analyzing daily news against all promises via Gemini...")
            
            batch_analysis = self.analyzer.batch_analyze_research_results(
                research_content=daily_news['content'],
                promises=promises
            )
            
            if batch_analysis.get('success'):
                print(f"  SUCCESS: Batch analysis complete")
                
                # Process each promise analysis
                for promise_analysis in batch_analysis.get('promises_analyzed', []):
                    if promise_analysis.get('is_mentioned') and promise_analysis.get('relevance_score', 0) > 0.5:
                        # Find the corresponding promise
                        promise_num = promise_analysis.get('promise_number', 0) - 1
                        if 0 <= promise_num < len(promises):
                            promise = promises[promise_num]
                            
                            update = {
                                'promise_id': promise.get('id'),
                                'promise_title': promise.get('title'),
                                'current_status': promise.get('status'),
                                'suggested_status': promise_analysis.get('suggested_status'),
                                'evidence': promise_analysis.get('current_evidence'),
                                'key_quote': promise_analysis.get('key_quote'),
                                'relevance_score': promise_analysis.get('relevance_score'),
                                'confidence': promise_analysis.get('status_confidence'),
                                'stance_change': promise_analysis.get('stance_change', False),
                                'stance_change_details': promise_analysis.get('stance_change_details'),
                                'source': 'daily_research',
                                'citations': daily_news.get('citations', []),
                                'timestamp': datetime.utcnow().isoformat()
                            }
                            
                            results['promise_updates'].append(update)
                            
                            # Check for status change
                            if (promise_analysis.get('suggested_status') and 
                                promise_analysis.get('suggested_status') != 'No Change' and
                                promise_analysis.get('suggested_status') != promise.get('status')):
                                
                                results['status_changes'].append({
                                    'promise_id': promise.get('id'),
                                    'promise_title': promise.get('title'),
                                    'old_status': promise.get('status'),
                                    'new_status': promise_analysis.get('suggested_status'),
                                    'evidence': promise_analysis.get('current_evidence'),
                                    'confidence': promise_analysis.get('status_confidence')
                                })
                            
                            # Check for stance change
                            if promise_analysis.get('stance_change'):
                                results['stance_changes_detected'].append({
                                    'promise_id': promise.get('id'),
                                    'promise_title': promise.get('title'),
                                    'details': promise_analysis.get('stance_change_details')
                                })
                
                # Add general observations
                results['general_observations'] = batch_analysis.get('general_observations')
                results['notable_stance_changes'] = batch_analysis.get('notable_stance_changes', [])
            else:
                results['errors'].append(f"Batch analysis failed: {batch_analysis.get('error')}")
                print(f"  ERROR: {batch_analysis.get('error')}")
        
        time.sleep(2)

        # Step 4: Research specific promises that need deeper investigation
        print("Step 4: Deep-diving into promises with potential updates...")
        for update in results['status_changes'][:5]:  # Limit to top 5 to avoid rate limits
            promise_id = update['promise_id']
            promise = next((p for p in promises if p.get('id') == promise_id), None)
            
            if promise:
                print(f"  Researching: {promise['title'][:50]}...")
                
                specific_research = self.researcher.research_specific_promise(
                    promise_title=promise['title'],
                    promise_description=promise['description'],
                    promise_category=promise.get('category', 'Other')
                )
                
                if specific_research['success']:
                    # Update the promise update with more detailed research
                    for pu in results['promise_updates']:
                        if pu['promise_id'] == promise_id:
                            pu['detailed_research'] = specific_research['content']
                            pu['detailed_citations'] = specific_research.get('citations', [])
                
                time.sleep(3)  # Rate limiting for specific research

        # Step 5: Generate summary
        print("Step 5: Generating research summary...")
        results['summary'] = self._generate_summary(results)
        
        results['completed'] = True
        results['promises_checked'] = len(promises)
        results['updates_found'] = len(results['promise_updates'])
        results['status_changes_found'] = len(results['status_changes'])
        
        print(f"[{datetime.now()}] Daily research complete!")
        print(f"  - Updates found: {results['updates_found']}")
        print(f"  - Status changes: {results['status_changes_found']}")
        print(f"  - Stance changes: {len(results['stance_changes_detected'])}")
        
        return results

    def _generate_summary(self, results: Dict) -> str:
        """Generate a human-readable summary of the research"""
        summary_parts = []
        
        date_str = datetime.now().strftime('%B %d, %Y')
        summary_parts.append(f"Daily Research Summary for {date_str}")
        summary_parts.append("=" * 50)
        
        if results['status_changes']:
            summary_parts.append(f"\n{len(results['status_changes'])} Status Changes Detected:")
            for change in results['status_changes']:
                summary_parts.append(f"  • {change['promise_title'][:50]}...")
                summary_parts.append(f"    {change['old_status']} → {change['new_status']}")
        
        if results['stance_changes_detected']:
            summary_parts.append(f"\n{len(results['stance_changes_detected'])} Stance Changes Detected:")
            for change in results['stance_changes_detected']:
                summary_parts.append(f"  • {change['promise_title'][:50]}...")
                summary_parts.append(f"    {change['details'][:100]}...")
        
        if results.get('general_observations'):
            summary_parts.append(f"\nGeneral Observations:")
            summary_parts.append(f"  {results['general_observations']}")
        
        if not results['status_changes'] and not results['stance_changes_detected']:
            summary_parts.append("\nNo significant changes detected in today's research.")
        
        if results['errors']:
            summary_parts.append(f"\nErrors encountered: {len(results['errors'])}")
        
        return "\n".join(summary_parts)

    def research_single_promise(self, promise: Dict) -> Dict:
        """
        Run focused research on a single promise.
        Useful for manual deep-dives or when a specific update is needed.
        """
        print(f"Researching: {promise['title']}")
        
        # Get specific research from Perplexity
        research = self.researcher.research_specific_promise(
            promise_title=promise['title'],
            promise_description=promise['description'],
            promise_category=promise.get('category', 'Other')
        )
        
        if not research['success']:
            return {
                'success': False,
                'error': research.get('error'),
                'promise_id': promise.get('id')
            }
        
        time.sleep(2)
        
        # Analyze with Gemini
        analysis = self.analyzer.analyze_news_for_promise(
            news_content=research['content'],
            news_source='Perplexity Research',
            promise_title=promise['title'],
            promise_description=promise['description'],
            current_status=promise.get('status', 'Unknown')
        )
        
        return {
            'success': True,
            'promise_id': promise.get('id'),
            'promise_title': promise['title'],
            'research': research,
            'analysis': analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
