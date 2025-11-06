# 🏛️ Mamdani Promise Tracker

A modern, real-time web application that tracks NYC Mayor-Elect Zohran Mamdani's campaign promises and analyzes their likelihood of being enacted using AI-powered analysis.

![Dashboard Preview](https://via.placeholder.com/800x400/0a0e1a/00ffff?text=Mamdani+Promise+Tracker)

## ✨ Features

### 🎯 Core Functionality
- **Promise Tracking**: Comprehensive database of all campaign promises
- **Real-Time Updates**: WebSocket-powered live notifications when promise status changes
- **AI Analysis**: Intelligent ranking system that evaluates likelihood of implementation
- **Auto-Scraping**: Automatically scans news sources every 6 hours for updates
- **Status Monitoring**: Track whether promises are delivered, in progress, failed, or not yet discussed

### 🤖 AI-Powered Analysis
The system analyzes multiple factors to rank promise likelihood:
- **Budget Feasibility**: Cost estimates and NYC's current budget situation
- **Legislative Complexity**: Whether it requires council, state, or federal approval
- **Political Alignment**: Compatibility with current political climate
- **Public Support**: Estimated public backing based on issue type
- **Category Priority**: How important the issue is in the current landscape

### 🌐 Data Sources (All Free!)
- Google News RSS feeds
- DuckDuckGo news search
- NYC official government websites
- Reddit discussions (r/nyc, r/newyorkcity, r/AskNYC)

### 🎨 Modern UI
- Sleek dark theme with neon accents
- Smooth animations and transitions
- Responsive design for all devices
- Real-time WebSocket notifications
- Interactive promise cards with detailed analysis

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**
```bash
cd mamdani_tracker
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv

# Activate on Linux/Mac:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database and start the app**
```bash
python app.py
```

The app will:
- Create the SQLite database
- Seed initial campaign promises
- Start the background scheduler
- Launch the web server on `http://localhost:5000`

## 📖 Usage

### Accessing the Dashboard
Open your browser and navigate to:
```
http://localhost:5000
```

### Features

#### 📊 Statistics Dashboard
- View total promises, delivered count, in-progress count
- See average likelihood score across all promises

#### 🔍 Filtering & Sorting
- **Filter by Category**: Housing, Transportation, Education, etc.
- **Filter by Status**: Not Yet In Office, In Progress, Delivered, Failed
- **Sort by**: Likelihood Rank, Likelihood Score, Date Made

#### 📝 Promise Details
Click any promise card to see:
- Full description and analysis
- Detailed likelihood breakdown
- All related news updates and sources
- Status change history

#### ⚡ Manual Scan
Click the "Scan Now" button to manually trigger a news scrape (useful for testing)

### Real-Time Notifications
The app will automatically show push notifications when:
- A promise status changes (e.g., from "Not Yet In Office" to "In Progress")
- New relevant news is found
- The app connects/disconnects from the server

## 🛠️ Technical Architecture

### Backend (Flask)
- **app.py**: Main Flask application with routes and WebSocket handlers
- **models.py**: SQLAlchemy database models (Promise, PromiseUpdate, ScrapeLog)
- **scraper.py**: Web scraping logic for multiple news sources
- **analyzer.py**: AI analysis engine for ranking promise likelihood
- **APScheduler**: Background job scheduler for automated scraping

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients, animations, and backdrop filters
- **Vanilla JavaScript**: No frameworks, lightweight and fast
- **Socket.IO**: Real-time WebSocket communication

### Database
- **SQLite**: Lightweight, file-based database (no separate server needed)
- **Tables**: promises, promise_update, scrape_log

## 📁 Project Structure

```
mamdani_tracker/
├── app.py                  # Main Flask application
├── models.py              # Database models
├── scraper.py             # Web scraping logic
├── analyzer.py            # AI analysis engine
├── requirements.txt       # Python dependencies
├── mamdani_tracker.db    # SQLite database (created on first run)
├── templates/
│   └── index.html        # Main dashboard template
└── static/
    ├── css/
    │   └── styles.css    # Modern dark theme styles
    └── js/
        └── app.js        # Frontend JavaScript
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for custom configuration:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### Scraping Interval
By default, the app scrapes every 6 hours. To change this, edit `app.py`:

```python
scheduler.add_job(
    func=scheduled_scrape,
    trigger='interval',
    hours=6,  # Change this value
    ...
)
```

## 📊 Initial Promises

The app comes pre-seeded with 10 known campaign promises:

1. Universal Free Public Transit
2. Massive Public Housing Expansion
3. Comprehensive Rent Control
4. Green New Deal for NYC
5. Fully Fund Public Schools
6. Medicare for All NYC
7. End Police Brutality and Qualified Immunity
8. Raise Minimum Wage to $25/hour
9. Expand Workers Rights and Union Protections
10. Close Rikers Island Immediately

Each promise includes AI analysis and likelihood scoring.

## 🔍 How the AI Analysis Works

The analyzer evaluates 5 key factors:

1. **Budget Score (20% weight)**
   - Analyzes cost keywords (billion, million, etc.)
   - Considers NYC's current budget climate
   - Higher score = more financially feasible

2. **Complexity Score (15% weight)**
   - Checks for legislative requirements
   - Identifies if state/federal approval needed
   - Higher score = easier to implement

3. **Political Alignment (30% weight)**
   - Matches promise with progressive/moderate keywords
   - Considers current City Council composition
   - Higher score = better political alignment

4. **Public Support (20% weight)**
   - Estimates based on issue type
   - Considers NYC-specific priorities
   - Higher score = more public backing

5. **Category Priority (15% weight)**
   - Rates importance in current climate
   - Housing and Public Safety rank highest
   - Category-specific multipliers applied

**Final Score**: Weighted average of all factors (0-1 scale, displayed as percentage)

## 🌐 API Endpoints

### GET `/api/promises`
Get all promises with optional filters
- Query params: `category`, `status`, `sort`
- Returns: JSON array of promises

### GET `/api/promises/<id>`
Get detailed promise information with updates
- Returns: Promise object with related updates

### GET `/api/stats`
Get dashboard statistics
- Returns: Total counts, breakdowns, last scrape info

### POST `/api/scrape/now`
Manually trigger a news scrape
- Returns: Success status and message

## 🚨 Troubleshooting

### Port 5000 Already in Use
Change the port in `app.py`:
```python
socketio.run(app, host='0.0.0.0', port=5001, ...)
```

### Scraping Not Working
- Check internet connection
- Some sources may be rate-limited
- Try manual scan to test

### Database Issues
Delete `mamdani_tracker.db` and restart the app to reinitialize

## 🔮 Future Enhancements

Potential features to add:
- [ ] Twitter/X API integration (when available)
- [ ] Email notification option
- [ ] Export data to CSV/JSON
- [ ] User accounts and custom alerts
- [ ] Mobile app version
- [ ] Comparison with other mayors
- [ ] Sentiment analysis graphs
- [ ] Historical promise tracking over time

## 📄 License

This project is open source and available for educational and research purposes.

## 🤝 Contributing

This is a monitoring and accountability tool. To add more promises or improve analysis:

1. Edit `seed_initial_promises()` in `app.py` to add more promises
2. Modify `analyzer.py` to adjust likelihood factors
3. Add more news sources in `scraper.py`

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. The AI analysis represents algorithmic estimates based on multiple factors and should not be considered definitive predictions. Promise information should be verified against official sources.

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review the code comments in each module
- All major functions are documented inline

---

**Built with**: Flask, SQLAlchemy, SocketIO, APScheduler, BeautifulSoup4

**Last Updated**: 2025

🗽 Tracking accountability in NYC government, one promise at a time.
