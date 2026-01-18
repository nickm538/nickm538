"""
AI-Powered Research Module using Perplexity Sonar API
Provides real-time, web-grounded research for Mamdani Promise Tracker

Enhanced for nuanced, real-world analysis with frank human perspective.
Not just tracking what's technically done - evaluating actual NYC impact.
"""
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import time


class PerplexityResearcher:
    """
    Uses Perplexity Sonar API for real-time news research with source citations.
    Enhanced to provide nuanced analysis that connects policy to real-world outcomes.
    """

    def __init__(self):
        self.api_key = os.environ.get('SONAR_API_KEY')
        if not self.api_key:
            raise ValueError("SONAR_API_KEY environment variable not set")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, messages: List[Dict], temperature: float = 0.3) -> Optional[Dict]:
        """Make a request to Perplexity API with error handling"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000,
            "return_citations": True,
            "return_related_questions": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Perplexity API error: {e}")
            return None

    def get_daily_mamdani_news(self) -> Dict:
        """
        Get comprehensive daily update on Mayor Mamdani with real-world context.
        Not just what happened - but what it actually means for NYC.
        """
        today = datetime.now().strftime("%B %d, %Y")
        
        messages = [
            {
                "role": "system",
                "content": """You are a seasoned NYC political analyst who's been covering city hall for 20 years. 
                You know how the city actually works - the difference between announcements and reality, 
                between policy on paper and what happens on the ground in the five boroughs.
                
                Your job is to give the real story - not PR spin, not opposition attacks, just honest 
                analysis of what's happening and what it means for regular New Yorkers.
                
                Be frank and conversational. If something sounds good but probably won't work, say so.
                If something is getting criticized unfairly, point that out too. Connect the dots between 
                policies and their real-world effects on housing, transit, jobs, safety, etc.
                
                Always cite your sources, but also provide context that helps people understand 
                the bigger picture."""
            },
            {
                "role": "user",
                "content": f"""Give me the real story on what's happening with Mayor Zohran Mamdani's 
                administration as of {today}.
                
                I want to know:
                
                1. **What actually happened** - Any official actions, announcements, executive orders, 
                   appointments, or policy moves. Not just press releases - what's actually being done.
                
                2. **The real-world impact** - How are these decisions affecting actual New Yorkers? 
                   What are people on the ground saying? Any early signs of whether policies are 
                   working or running into problems?
                
                3. **The political reality** - What's the City Council saying? Albany? Any pushback 
                   or support from unions, business groups, community organizations? What are the 
                   actual chances of his agenda moving forward?
                
                4. **Reading between the lines** - What's the administration signaling about priorities? 
                   Any shifts from campaign rhetoric to governing reality? Things that technically 
                   happened but might not pan out as advertised?
                
                5. **What to watch** - What's coming up that could be significant? Budget battles, 
                   legislation, court challenges, etc.
                
                Be honest and direct. If there's not much news, say so. If something is being 
                overhyped or undercovered, point that out.
                
                Include source URLs for everything factual."""
            }
        ]

        result = self._make_request(messages, temperature=0.4)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                'success': True,
                'content': content,
                'citations': citations,
                'timestamp': datetime.utcnow().isoformat(),
                'query_type': 'daily_update'
            }
        
        return {
            'success': False,
            'error': 'Failed to get response from Perplexity API',
            'timestamp': datetime.utcnow().isoformat()
        }

    def research_specific_promise(self, promise_title: str, promise_description: str, 
                                   promise_category: str) -> Dict:
        """
        Deep-dive research on a specific campaign promise with real-world assessment.
        """
        messages = [
            {
                "role": "system",
                "content": """You're a veteran NYC policy analyst who's seen a lot of mayors come and go.
                You know the difference between campaign promises and governing realities.
                
                Your job is to give an honest assessment - not cheerleading, not doom-saying.
                What's actually happening with this promise? What are the real obstacles?
                What would it actually take to make this happen in NYC?
                
                Be specific about NYC's unique challenges - the MTA relationship with Albany,
                the city budget constraints, the political dynamics, the bureaucracy, etc.
                
                If something is technically possible but practically unlikely, say so.
                If something is getting unfair criticism, point that out too."""
            },
            {
                "role": "user",
                "content": f"""Give me the real assessment on this Mamdani campaign promise:

                **PROMISE:** {promise_title}
                **DETAILS:** {promise_description}
                **CATEGORY:** {promise_category}

                I want to know:

                1. **Current Status** - What has actually been done on this? Any executive orders,
                   legislation introduced, task forces formed, budget allocations? Or is it still
                   just talk?

                2. **Real-World Progress** - Beyond announcements, is anything actually changing
                   on the ground? Any early implementation? Pilot programs?

                3. **The Obstacles** - What's standing in the way? Budget? Albany? City Council?
                   Federal law? Unions? Business opposition? Logistics? Be specific about what
                   would need to happen for this to actually work.

                4. **Honest Assessment** - Based on what you're seeing, what are the actual chances
                   this gets done? Is the administration serious about it or is it back-burner?
                   Any signs they're walking it back or doubling down?

                5. **What Success Would Look Like** - If this actually happened, what would
                   New Yorkers actually experience differently? And what are the potential
                   downsides or unintended consequences nobody's talking about?

                Be frank. If this promise was always unrealistic, say so. If it's more achievable
                than critics claim, explain why. Give me the nuanced take.
                
                Include source URLs for all factual claims."""
            }
        ]

        result = self._make_request(messages, temperature=0.4)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                'success': True,
                'promise_title': promise_title,
                'content': content,
                'citations': citations,
                'timestamp': datetime.utcnow().isoformat(),
                'query_type': 'promise_specific'
            }
        
        return {
            'success': False,
            'promise_title': promise_title,
            'error': 'Failed to get response from Perplexity API',
            'timestamp': datetime.utcnow().isoformat()
        }

    def detect_stance_changes(self) -> Dict:
        """
        Track any shifts between campaign rhetoric and governing reality.
        The nuanced stuff - not just flip-flops, but evolution and pragmatic adjustments.
        """
        messages = [
            {
                "role": "system",
                "content": """You're a political journalist who covers the gap between campaigns and governing.
                You understand that some "flip-flops" are actually reasonable adjustments to reality,
                while others are genuine betrayals of voter trust. Your job is to distinguish between them.
                
                Look for:
                - Outright reversals (promised X, now doing opposite)
                - Quiet walkbacks (promised X, now not mentioning it)
                - Pragmatic adjustments (promised X, now doing X-lite because of real constraints)
                - Rhetorical shifts (same policy, different framing)
                - Priority changes (still supports X, but clearly focused on Y instead)
                
                Be fair but honest. Politicians do have to adjust to reality, but voters deserve
                to know when promises are being abandoned vs. adapted."""
            },
            {
                "role": "user",
                "content": """Analyze any shifts between Mayor Zohran Mamdani's campaign positions 
                and his current governing approach.

                I want the nuanced take:

                1. **Clear Reversals** - Has he explicitly abandoned or reversed any campaign positions?
                   What did he say then vs. now? Is there a legitimate reason or is this a betrayal?

                2. **Quiet Walkbacks** - Any promises he's just... stopped talking about? Things that
                   were prominent in the campaign but have disappeared from his agenda?

                3. **Pragmatic Adjustments** - Where has he scaled back ambitions in ways that might
                   actually be reasonable given the constraints of the job? What's the difference
                   between the campaign version and the governing version?

                4. **Rhetorical Evolution** - Is he framing things differently now? More moderate
                   language? Different emphasis? What does that signal?

                5. **Priority Shifts** - What's he actually spending his time and political capital on
                   vs. what he emphasized in the campaign? Any surprises?

                Be balanced. Some evolution is normal and even healthy. But voters should know
                what's changed and why. Don't be a cheerleader or a hater - just give the honest read.
                
                Include sources for all specific claims."""
            }
        ]

        result = self._make_request(messages, temperature=0.4)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                'success': True,
                'content': content,
                'citations': citations,
                'timestamp': datetime.utcnow().isoformat(),
                'query_type': 'stance_changes'
            }
        
        return {
            'success': False,
            'error': 'Failed to get response from Perplexity API',
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_nyc_impact_analysis(self) -> Dict:
        """
        Analyze how Mamdani's policies are actually affecting NYC - the real-world outcomes.
        """
        messages = [
            {
                "role": "system",
                "content": """You're an urban policy expert who focuses on what actually happens
                in cities, not what politicians say will happen. You look at data, talk to people
                on the ground, and connect policy decisions to real outcomes.
                
                Your expertise is in understanding how NYC actually works - the complex interplay
                of city agencies, state control over the MTA, federal funding, union contracts,
                real estate dynamics, neighborhood politics, etc.
                
                Give the honest assessment of what's working, what's not, and what's too early to tell."""
            },
            {
                "role": "user",
                "content": """How are Mayor Mamdani's policies actually affecting New York City?

                Give me the real-world impact assessment:

                1. **Housing** - Any actual changes in affordability, availability, tenant protections?
                   What are renters and landlords experiencing? Any new construction or preservation?

                2. **Transit** - What's happening with subways, buses, bike infrastructure?
                   Any service changes? Fare policy? MTA relationship?

                3. **Public Safety** - Crime trends, NYPD policies, community relations?
                   What are different neighborhoods experiencing?

                4. **Economy & Jobs** - Business climate, employment, minimum wage effects?
                   What are workers and employers saying?

                5. **Quality of Life** - Parks, sanitation, homelessness, street conditions?
                   The everyday stuff New Yorkers notice.

                6. **Who's Winning, Who's Losing** - Be honest about distributional effects.
                   Which New Yorkers are benefiting from his policies? Which are being hurt?
                   Any unintended consequences?

                I want the ground-level reality, not the press release version. What would
                someone living in the Bronx, Brooklyn, Queens, Manhattan, or Staten Island
                actually be experiencing differently?
                
                Include sources."""
            }
        ]

        result = self._make_request(messages, temperature=0.4)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                'success': True,
                'content': content,
                'citations': citations,
                'timestamp': datetime.utcnow().isoformat(),
                'query_type': 'nyc_impact'
            }
        
        return {
            'success': False,
            'error': 'Failed to get response from Perplexity API',
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_multi_perspective_view(self, topic: str) -> Dict:
        """
        Get comprehensive views from multiple perspectives to minimize bias.
        """
        messages = [
            {
                "role": "system",
                "content": """You're a balanced journalist who believes readers deserve to hear
                all sides of an issue, not just the one that confirms their priors.
                
                Your job is to present multiple legitimate perspectives fairly, even ones you
                might personally disagree with. Help people understand WHY different groups
                see things differently - not just THAT they disagree.
                
                Avoid false balance (not every issue has two equal sides), but do give voice
                to the range of reasonable perspectives on genuinely contested issues."""
            },
            {
                "role": "user",
                "content": f"""Give me the full spectrum of perspectives on: {topic}

                I want to understand how different New Yorkers see this:

                1. **The Administration's View** - What is Mamdani's team saying? What's their
                   argument for why this is the right approach?

                2. **Progressive Allies** - What do his supporters on the left think? Are they
                   satisfied or pushing for more?

                3. **Moderate/Centrist Take** - What do more moderate Democrats and independents
                   think? What are their concerns?

                4. **Conservative/Business Critique** - What are Republicans and business groups
                   saying? What are their specific objections?

                5. **Affected Communities** - What are the people most directly affected saying?
                   This might be different from what political leaders claim they want.

                6. **Expert Analysis** - What do policy experts, academics, or people with
                   relevant professional experience say? Any data or evidence being cited?

                7. **Your Assessment** - After hearing all sides, what's your honest take?
                   Who has the stronger argument? What's being overlooked by all sides?

                Be fair to each perspective while still being willing to say when someone's
                argument is weak or when the evidence points in a particular direction.
                
                Include sources."""
            }
        ]

        result = self._make_request(messages, temperature=0.4)
        
        if result and 'choices' in result:
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                'success': True,
                'topic': topic,
                'content': content,
                'citations': citations,
                'timestamp': datetime.utcnow().isoformat(),
                'query_type': 'multi_perspective'
            }
        
        return {
            'success': False,
            'topic': topic,
            'error': 'Failed to get response from Perplexity API',
            'timestamp': datetime.utcnow().isoformat()
        }

    def run_full_daily_research(self, promises: List[Dict]) -> Dict:
        """
        Run comprehensive daily research covering all aspects.
        Enhanced for nuanced, real-world analysis.
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'daily_news': None,
            'stance_changes': None,
            'nyc_impact': None,
            'promise_updates': [],
            'errors': []
        }

        # 1. Get daily news with real-world context
        print("Fetching daily Mamdani news with real-world analysis...")
        daily_news = self.get_daily_mamdani_news()
        results['daily_news'] = daily_news
        if not daily_news['success']:
            results['errors'].append('Failed to fetch daily news')
        time.sleep(2)

        # 2. Check for stance changes
        print("Analyzing stance changes and evolution...")
        stance_changes = self.detect_stance_changes()
        results['stance_changes'] = stance_changes
        if not stance_changes['success']:
            results['errors'].append('Failed to check stance changes')
        time.sleep(2)

        # 3. Get NYC impact analysis
        print("Assessing real-world NYC impact...")
        nyc_impact = self.get_nyc_impact_analysis()
        results['nyc_impact'] = nyc_impact
        if not nyc_impact['success']:
            results['errors'].append('Failed to get NYC impact analysis')
        time.sleep(2)

        # 4. Research specific promises (top 5 to avoid rate limits)
        print(f"Deep-diving into {min(5, len(promises))} key promises...")
        for i, promise in enumerate(promises[:5]):
            print(f"  Researching: {promise['title'][:50]}...")
            
            promise_result = self.research_specific_promise(
                promise_title=promise['title'],
                promise_description=promise['description'],
                promise_category=promise.get('category', 'Other')
            )
            results['promise_updates'].append(promise_result)
            
            if not promise_result['success']:
                results['errors'].append(f"Failed to research: {promise['title']}")
            
            time.sleep(3)

        results['completed'] = True
        results['promises_researched'] = len(results['promise_updates'])
        
        return results
