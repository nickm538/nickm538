"""
Main Flask application for Mamdani Tracker.

Features:
- Flask web server with Socket.IO for real-time updates
- SQLAlchemy database with SQLite (dev) or PostgreSQL (production)
- APScheduler for background scraping jobs
- Environment-based configuration
- Comprehensive logging
"""
import os
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from mamdani_tracker.models import db, Promise, NewsArticle
from mamdani_tracker.analyzer import analyze_promise
from mamdani_tracker.scraper import scrape_all_sources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__,
           template_folder='../templates',
           static_folder='../static')

# Configuration from environment with sensible defaults
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 
    'sqlite:///mamdani_tracker.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Note: For production, use PostgreSQL instead of SQLite
# SQLite has concurrency limitations that can cause issues with background jobs
# Set SQLALCHEMY_DATABASE_URI to: postgresql://user:pass@host/dbname
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'].lower():
    logger.warning("Using SQLite database. For production, consider PostgreSQL for better concurrency.")

# Initialize extensions
db.init_app(app)

# Initialize SocketIO with threading for async support
# For production, consider using gevent (install: pip install gevent)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global scheduler instance
scheduler = None


def init_database():
    """Initialize database and seed with sample promises."""
    with app.app_context():
        db.create_all()
        
        # Check if we already have data
        if Promise.query.count() == 0:
            logger.info("Seeding database with sample promises")
            
            sample_promises = [
                {
                    'title': 'Expand Public Transportation',
                    'description': 'Build 50 new miles of light rail and add 100 electric buses to the public transit system.',
                    'category': 'Infrastructure',
                    'date_made': datetime(2024, 1, 15, tzinfo=timezone.utc),
                    'status': 'In Progress',
                    'budget_required': 500.0,
                    'legislative_complexity': 3,
                    'public_interest': 8,
                    'deadline_days': 730
                },
                {
                    'title': 'Reduce Healthcare Costs',
                    'description': 'Implement measures to reduce prescription drug costs by 20% for seniors.',
                    'category': 'Healthcare',
                    'date_made': datetime(2024, 2, 1, tzinfo=timezone.utc),
                    'status': 'Not Started',
                    'budget_required': 200.0,
                    'legislative_complexity': 4,
                    'public_interest': 10,
                    'deadline_days': 365
                },
                {
                    'title': 'Climate Action Plan',
                    'description': 'Transition to 100% renewable energy for government buildings by 2030.',
                    'category': 'Environment',
                    'date_made': datetime(2024, 3, 10, tzinfo=timezone.utc),
                    'status': 'In Progress',
                    'budget_required': 1000.0,
                    'legislative_complexity': 5,
                    'public_interest': 9,
                    'deadline_days': 1825
                },
                {
                    'title': 'Education Reform',
                    'description': 'Increase teacher salaries by 15% and reduce class sizes to a maximum of 20 students.',
                    'category': 'Education',
                    'date_made': datetime(2024, 4, 5, tzinfo=timezone.utc),
                    'status': 'Not Started',
                    'budget_required': 300.0,
                    'legislative_complexity': 3,
                    'public_interest': 7,
                    'deadline_days': 540
                },
                {
                    'title': 'Affordable Housing Initiative',
                    'description': 'Build 5,000 affordable housing units over the next 3 years.',
                    'category': 'Housing',
                    'date_made': datetime(2024, 5, 20, tzinfo=timezone.utc),
                    'status': 'Not Started',
                    'budget_required': 750.0,
                    'legislative_complexity': 4,
                    'public_interest': 9,
                    'deadline_days': 1095
                },
                {
                    'title': 'Small Business Support',
                    'description': 'Create a $50M fund for low-interest loans to small businesses.',
                    'category': 'Economy',
                    'date_made': datetime(2024, 6, 1, tzinfo=timezone.utc),
                    'status': 'Completed',
                    'budget_required': 50.0,
                    'legislative_complexity': 2,
                    'public_interest': 6,
                    'deadline_days': None
                }
            ]
            
            for promise_data in sample_promises:
                promise = Promise(**promise_data)
                # Analyze and calculate scores
                promise = analyze_promise(promise)
                db.session.add(promise)
            
            db.session.commit()
            logger.info(f"Seeded {len(sample_promises)} promises")
        else:
            logger.info(f"Database already contains {Promise.query.count()} promises")


def scrape_news_background():
    """
    Background job to scrape news articles.
    
    This runs periodically to fetch new articles related to promises.
    Uses app context to access database.
    """
    with app.app_context():
        try:
            logger.info("Starting background news scraping job")
            
            # Get all promises
            promises = Promise.query.all()
            
            for promise in promises:
                try:
                    # Scrape news for this promise
                    query = f"{promise.title} {promise.category}"
                    articles = scrape_all_sources(query, max_per_source=3)
                    
                    # Save articles to database
                    new_count = 0
                    for article_data in articles:
                        # Check if article already exists (by URL)
                        existing = NewsArticle.query.filter_by(url=article_data['url']).first()
                        if not existing:
                            article = NewsArticle(
                                title=article_data['title'],
                                url=article_data['url'],
                                source=article_data['source'],
                                snippet=article_data.get('snippet', ''),
                                published_date=article_data.get('published_date'),
                                promise_id=promise.id
                            )
                            db.session.add(article)
                            new_count += 1
                    
                    if new_count > 0:
                        db.session.commit()
                        logger.info(f"Saved {new_count} new articles for promise: {promise.title}")
                        
                        # Emit Socket.IO event for real-time updates
                        try:
                            socketio.emit('news_update', {
                                'promise_id': promise.id,
                                'new_articles': new_count
                            })
                        except Exception as e:
                            logger.warning(f"Could not emit Socket.IO event: {e}")
                    
                except Exception as e:
                    logger.error(f"Error scraping for promise '{promise.title}': {e}")
                    continue
            
            logger.info("Completed background news scraping job")
            
        except Exception as e:
            logger.error(f"Error in background scraping job: {e}")


def init_scheduler():
    """Initialize APScheduler for background jobs."""
    global scheduler
    
    # Check if scheduler is already running
    if scheduler is not None and scheduler.running:
        logger.info("Scheduler already running")
        return scheduler
    
    try:
        scheduler = BackgroundScheduler()
        
        # Add job to scrape news every 6 hours
        # For development/testing, you might want to reduce this interval
        scheduler.add_job(
            func=scrape_news_background,
            trigger=IntervalTrigger(hours=6),
            id='scrape_news_job',
            name='Scrape news articles',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler started successfully")
        
        return scheduler
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")
        return None


# Flask routes

@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')


@app.route('/api/promises')
def get_promises():
    """Get all promises with their scores."""
    try:
        promises = Promise.query.all()
        return jsonify({
            'success': True,
            'promises': [p.to_dict() for p in promises]
        })
    except Exception as e:
        logger.error(f"Error fetching promises: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/promises/<int:promise_id>')
def get_promise(promise_id):
    """Get a specific promise with related articles."""
    try:
        promise = Promise.query.get_or_404(promise_id)
        articles = NewsArticle.query.filter_by(promise_id=promise_id).order_by(
            NewsArticle.scraped_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'promise': promise.to_dict(),
            'articles': [a.to_dict() for a in articles]
        })
    except Exception as e:
        logger.error(f"Error fetching promise {promise_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    """Manually trigger a news scraping job."""
    try:
        # Run scraping in background (non-blocking)
        # In production, consider using a task queue like Celery
        import threading
        thread = threading.Thread(target=scrape_news_background)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Scraping job started'
        })
    except Exception as e:
        logger.error(f"Error triggering scrape: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Socket.IO events

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to Mamdani Tracker'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('request_update')
def handle_update_request():
    """Handle client request for data update."""
    try:
        promises = Promise.query.all()
        emit('promises_update', {
            'promises': [p.to_dict() for p in promises]
        })
    except Exception as e:
        logger.error(f"Error handling update request: {e}")
        emit('error', {'message': str(e)})


def create_app():
    """Application factory for creating the Flask app."""
    init_database()
    init_scheduler()
    return app


if __name__ == '__main__':
    # Initialize app
    app_instance = create_app()
    
    # Get host and port from environment or use defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Mamdani Tracker on {host}:{port}")
    logger.info(f"Access from iPhone: Use http://<your-computer-ip>:{port}")
    
    # Run with SocketIO
    # eventlet is recommended for production-like async support
    socketio.run(app_instance, host=host, port=port, debug=debug)
