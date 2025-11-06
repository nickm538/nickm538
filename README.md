# Mamdani Tracker

A production-ready political promise tracking application with real-time news scraping and analysis capabilities.

## Features

- 📊 **Promise Dashboard** - Track political promises with comprehensive scoring and analysis
- 🔍 **Real-time News Scraping** - Automatically fetch related news from Google News, DuckDuckGo, and Reddit
- 📈 **Smart Analytics** - Multi-dimensional scoring system (priority, feasibility, impact, urgency)
- 🔄 **Live Updates** - Socket.IO integration for real-time data synchronization
- 🎨 **Modern UI** - Bootstrap 5 with dark/light theme toggle
- 📱 **Mobile-Friendly** - Responsive design works great on phones and tablets

## Screenshots

The application features a modern card-based interface with real-time updates and comprehensive promise analysis.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Optional: Docker for containerized deployment

### Local Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nickm538/nickm538.git
cd nickm538
```

2. **Create and activate a virtual environment:**
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python run.py
```

The application will start on `http://localhost:5000`

### Alternative: Run as a Module

You can also run the app as a Python module:
```bash
python -m mamdani_tracker.app
```

## Testing from an iPhone (or any mobile device)

### Method 1: Same Wi-Fi Network (Recommended for local testing)

1. **Find your computer's local IP address:**

   On **macOS/Linux**:
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   
   On **Windows**:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter (usually something like `192.168.1.x`)

2. **Start the app with host binding:**
   ```bash
   # The app already binds to 0.0.0.0 by default, so just run:
   python run.py
   ```

3. **Access from your iPhone:**
   - Connect your iPhone to the **same Wi-Fi network** as your computer
   - Open Safari or any browser on your iPhone
   - Navigate to: `http://YOUR_COMPUTER_IP:5000`
   - Example: `http://192.168.1.100:5000`

### Method 2: Using ngrok (For remote testing or different networks)

[ngrok](https://ngrok.com/) creates a secure tunnel to your local server, perfect for testing from anywhere.

1. **Install ngrok:**
   - Download from [ngrok.com](https://ngrok.com/download)
   - Or via Homebrew: `brew install ngrok/ngrok/ngrok` (macOS)

2. **Start your app:**
   ```bash
   python run.py
   ```

3. **In a separate terminal, start ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **Access from your iPhone:**
   - ngrok will display a public URL like: `https://abc123.ngrok.io`
   - Open this URL in your iPhone's browser
   - You can now access your app from anywhere!

**Note:** Free ngrok URLs expire after 2 hours and change each time you restart ngrok.

## Environment Configuration

You can customize the application using environment variables:

```bash
# Secret key for Flask sessions (change in production!)
export SECRET_KEY="your-secret-key-here"

# Database URI (SQLite by default, use PostgreSQL for production)
export SQLALCHEMY_DATABASE_URI="sqlite:///mamdani_tracker.db"
# For PostgreSQL: "postgresql://user:password@localhost/mamdani_tracker"

# Server configuration
export FLASK_HOST="0.0.0.0"  # Default: binds to all interfaces
export FLASK_PORT="5000"      # Default: 5000
export FLASK_DEBUG="False"    # Set to "False" in production
```

## Docker Deployment

For containerized deployment:

1. **Build the Docker image:**
```bash
docker build -t mamdani-tracker .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 \
  -e SECRET_KEY="your-secret-key" \
  -e SQLALCHEMY_DATABASE_URI="sqlite:///mamdani_tracker.db" \
  mamdani-tracker
```

3. **Using Docker Compose:**
Create a `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=change-this-in-production
      - SQLALCHEMY_DATABASE_URI=postgresql://user:pass@db/mamdani
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mamdani
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Then run:
```bash
docker-compose up
```

## Project Structure

```
nickm538/
├── mamdani_tracker/          # Main application package
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask application & Socket.IO
│   ├── models.py            # Database models
│   ├── scraper.py           # News scraping with retry logic
│   └── analyzer.py          # Promise scoring algorithms
├── templates/               # HTML templates
│   └── index.html          # Main dashboard
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css      # Custom styles
│   └── js/
│       └── app.js          # Frontend JavaScript
├── tests/                   # Test suite
│   └── test_analyzer.py    # Analyzer unit tests
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Architecture & Features

### Database Models

- **Promise**: Tracks political promises with scoring metrics
- **NewsArticle**: Stores scraped news articles linked to promises

All timestamps use UTC for consistency.

### Scraper System

The scraper uses robust HTTP handling:
- `requests.Session` with automatic retry logic (3 retries with exponential backoff)
- Configurable timeouts (5s connect, 15s read)
- Descriptive User-Agent header
- Rate limiting with sleep delays between requests
- Safe parsing with error handling

**Supported sources:**
- Google News RSS (public feed)
- DuckDuckGo HTML search results
- Reddit JSON API (public, no OAuth)

**Production Note:** For reliable production use, consider using official APIs with proper authentication:
- Google News API with API key
- Reddit API with OAuth (using PRAW library)
- Twitter API for social media mentions

### Analyzer System

Multi-dimensional scoring system with all scores clamped to [0.0, 1.0]:

- **Priority Score**: Based on public interest vs. budget requirements
- **Feasibility Score**: Considers budget and legislative complexity
- **Impact Score**: Evaluates potential impact on public interest and scale
- **Urgency Score**: Time-based urgency from deadline proximity
- **Overall Score**: Weighted average (30% priority, 25% feasibility, 25% impact, 20% urgency)

All calculations include error handling and default to neutral scores (0.5) on errors.

### Background Jobs

APScheduler runs periodic tasks:
- News scraping every 6 hours (configurable)
- Automatic database updates
- Real-time Socket.IO notifications for new articles

**Concurrency Note:** SQLite has limitations with concurrent writes. For production with heavy traffic, use PostgreSQL:
```bash
export SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost/mamdani_tracker"
```

### Real-time Updates

Socket.IO provides live updates:
- Connection status indicator
- Automatic promise updates
- New article notifications
- Manual scrape triggers

## API Endpoints

### REST API

- `GET /` - Main dashboard
- `GET /api/promises` - Fetch all promises with scores
- `GET /api/promises/<id>` - Get specific promise with related articles
- `POST /api/scrape` - Manually trigger news scraping

### Socket.IO Events

- `connect` - Client connection established
- `disconnect` - Client disconnected
- `news_update` - New articles scraped (server → client)
- `promises_update` - Promise data updated (server → client)
- `request_update` - Client requests data refresh (client → server)

## Running Tests

Run the test suite:
```bash
python -m pytest tests/
```

Or run specific tests:
```bash
python -m pytest tests/test_analyzer.py -v
```

Run with coverage:
```bash
python -m pytest tests/ --cov=mamdani_tracker --cov-report=html
```

## Security Considerations

### Implemented

- ✅ Input sanitization and HTML escaping in templates
- ✅ Environment-based secret key configuration
- ✅ CSRF protection via Flask-WTF (for forms)
- ✅ Content Security Policy headers recommended
- ✅ No hardcoded credentials
- ✅ Secure password hashing (if user auth added)

### Recommendations

1. **Change SECRET_KEY in production** - Use a strong random key
2. **Use PostgreSQL in production** - Better concurrency and reliability
3. **Enable HTTPS** - Use a reverse proxy (nginx) with SSL certificates
4. **Rate limiting** - Implement rate limits on API endpoints
5. **Input validation** - Add comprehensive input validation for user data
6. **API authentication** - Add authentication for API endpoints if exposing publicly
7. **Content Security Policy** - Add CSP headers to prevent XSS attacks

### XSS Prevention

The frontend uses `escapeHtml()` to sanitize all user-generated content before rendering. However, review any changes that display external content.

## Production Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable to a strong random value
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper logging and monitoring
- [ ] Set up automated backups for the database
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Review and apply security headers
- [ ] Consider using official APIs with OAuth for news sources
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Configure production WSGI server (e.g., gunicorn)

## Troubleshooting

### App won't start

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)
- Verify virtual environment is activated

### Can't access from iPhone

- Ensure both devices are on the same Wi-Fi network
- Check firewall settings on your computer
- Verify the app is running with `host='0.0.0.0'` (default)
- Try pinging your computer's IP from another device

### Scraping errors

- Check internet connection
- Some sources may have rate limits - wait a few minutes
- DuckDuckGo may block automated requests - this is expected
- Consider implementing proxy rotation for production

### Database errors

- Delete the database file and restart: `rm mamdani_tracker.db && python run.py`
- Check write permissions in the application directory
- For SQLite concurrency issues, switch to PostgreSQL

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with appropriate tests
4. Run tests: `python -m pytest tests/`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/my-feature`
7. Submit a pull request

## License

This project is created for educational purposes. Please respect the terms of service of any third-party APIs used.

## Acknowledgments

- Built with Flask and Bootstrap 5
- News sources: Google News, DuckDuckGo, Reddit
- Icons from Bootstrap Icons
- Real-time updates powered by Socket.IO

---

**Happy tracking!** 📊✨
