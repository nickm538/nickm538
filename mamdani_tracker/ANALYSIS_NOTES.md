# Mamdani Tracker - System Analysis Notes

## Issues Identified

### 1. **Scraper Limitations (Critical)**
- **Google News RSS**: SSL errors occurring intermittently
- **NYC Official Sites**: Returns 0 results - search URL pattern doesn't work for nyc.gov
- **Reddit API**: Works but returns rate-limited (429) responses without proper User-Agent
- **DuckDuckGo**: Works but returns general search results, not news-specific
- **No API-based news source**: Relies entirely on web scraping which is fragile

### 2. **Article Relevance Matching (Major)**
- Uses simple keyword matching (words > 3 chars from title)
- Cannot understand context or nuance
- Example: "transit" in article about "transit of Venus" would match transit promises
- No semantic understanding of whether article actually relates to promise fulfillment

### 3. **Status Change Detection (Major)**
- Hardcoded keyword lists for sentiment/status detection
- "approved" → Delivered, but what if "approved for study" (not delivered)?
- Cannot distinguish between:
  - Promise announced vs. promise in progress vs. promise delivered
  - Pre-election stance vs. post-election stance changes
  - Actual policy action vs. just talking about it

### 4. **Analyzer Module (Minor)**
- Static political context values (hardcoded 2025 assumptions)
- No real-time political climate assessment
- Keyword-based budget/complexity analysis is simplistic

### 5. **Data Quality Issues**
- `source_url` in seed data all point to `https://example.com/campaign`
- No actual campaign promise sources documented
- No mechanism to verify/update promise accuracy

### 6. **Missing Features for Production**
- No daily scheduled API-based research
- No stance change tracking (pre vs post election)
- No bias filtering mechanism
- No source credibility scoring

## Recommended API Integration Architecture

### Perplexity Sonar (Real-time Research)
- Daily query: "What actions has NYC Mayor Zohran Mamdani taken in the last 24 hours?"
- Promise-specific queries: "Has Mamdani made progress on [promise topic]?"
- Returns sourced, factual information with citations

### OpenAI GPT (Intelligent Analysis)
- Analyze if news article actually relates to specific promise
- Detect stance changes (what he said before vs. now)
- Determine status: Not Started, In Progress, Delivered, Broken, Stance Changed
- Filter noise and bias from sources
- Generate nuanced analysis text

## Files to Create/Modify

1. `ai_research.py` - New module for Perplexity Sonar integration
2. `ai_analyzer.py` - New module for OpenAI-powered analysis
3. `scraper.py` - Update to use AI research as primary source
4. `analyzer.py` - Update to use AI for analysis
5. `app.py` - Update scheduler for daily API research
