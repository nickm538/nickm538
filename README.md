# Mamdani Tracker

A comprehensive web application for tracking and analyzing political promises with real-time updates, intelligent scoring, and robust web scraping.

## Features

- **Robust Web Scraping**: Scrapes political news from Google News RSS, DuckDuckGo, and Reddit with retry logic and error handling
- **Intelligent Analysis**: Automatically scores promises based on feasibility, impact, priority, budget requirements, and legislative complexity
- **Real-time Updates**: Socket.IO integration provides live updates when new promises are discovered
- **Modern Dashboard**: Bootstrap 5-based responsive UI with dark/light theme toggle
- **RESTful API**: JSON endpoints for programmatic access to promises
- **Background Jobs**: APScheduler runs periodic scraping tasks
- **Production-Ready**: Environment-based configuration, logging, and Docker support

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py

# 4. Open browser to http://localhost:5000
```

## Testing from iPhone

### Same Wi-Fi Network

1. Find your computer's IP address:
   - macOS: `ipconfig getifaddr en0`
   - Linux: `hostname -I | awk '{print $1}'`
   - Windows: `ipconfig` (look for IPv4 Address)

2. Run the app: `python run.py`

3. On iPhone, go to: `http://YOUR_IP:5000`

### Using ngrok (External Access)

```bash
# Install ngrok from ngrok.com
ngrok http 5000

# Use the provided https URL on your iPhone
```

## Configuration

Set environment variables:

```bash
export SECRET_KEY="your-secret-key"
export SQLALCHEMY_DATABASE_URI="sqlite:///mamdani_tracker.db"
```

**For production, use PostgreSQL instead of SQLite:**

```bash
export SQLALCHEMY_DATABASE_URI="postgresql://user:pass@host/db"
```

## API Endpoints

- `GET /api/promises` - Get all promises
- `GET /api/promises/<id>` - Get single promise
- `POST /api/scrape/now` - Trigger manual scrape

## Running Tests

```bash
python -m unittest discover tests -v
```

## Docker

```bash
docker build -t mamdani-tracker .
docker run -p 5000:5000 mamdani-tracker
```

## License

Educational project - respect website terms of service when scraping.
