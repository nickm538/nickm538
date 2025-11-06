"""
Main Flask application for Mamdani Tracker.

This module sets up:
- Flask app with environment-based configuration
- SQLAlchemy database
- Flask-SocketIO for real-time updates
- APScheduler for background scraping
- API endpoints for promises and manual scraping
- Python logging throughout
"""
import logging
import os
from datetime import datetime, timezone

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from mamdani_tracker.models import db, Promise
from mamdani_tracker.scraper import scrape_all_sources
from mamdani_tracker.analyzer import update_promise_scores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get the root directory of the project (parent of mamdani_tracker package)
import pathlib
ROOT_DIR = pathlib.Path(__file__).parent.parent

# Create Flask app with correct paths
app = Flask(
    __name__,
    template_folder=str(ROOT_DIR / 'templates'),
    static_folder=str(ROOT_DIR / 'static')
)

# Configuration from environment with sensible defaults
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'sqlite:///mamdani_tracker.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using
    'pool_recycle': 300,    # Recycle connections after 5 minutes
}

# NOTE: For production, use PostgreSQL instead of SQLite
# Set environment variable: SQLALCHEMY_DATABASE_URI=postgresql://user:pass@localhost/dbname
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI'].lower():
    logger.warning(
        "Using SQLite database. For production, use PostgreSQL "
        "via SQLALCHEMY_DATABASE_URI environment variable."
    )

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global scheduler reference
scheduler = None


def scrape_and_analyze():
    """
    Background job to scrape sources and analyze promises.
    
    This function runs periodically to fetch new data.
    NOTE: SQLite has concurrency limitations. For production use PostgreSQL.
    """
    with app.app_context():
        try:
            logger.info("Starting scheduled scrape and analysis")
            
            # Scrape all sources
            results = scrape_all_sources("political promises")
            
            if not results:
                logger.warning("No results from scraping")
                return
            
            # Process each result
            new_count = 0
            updated_count = 0
            
            for result in results:
                try:
                    # Check if promise already exists by title
                    existing = Promise.query.filter_by(title=result['title']).first()
                    
                    if existing:
                        # Update existing promise
                        existing.description = result.get('description', existing.description)
                        existing.source_url = result.get('source_url', existing.source_url)
                        existing.updated_at = datetime.now(timezone.utc)
                        update_promise_scores(existing)
                        updated_count += 1
                        logger.debug(f"Updated promise: {existing.title[:50]}...")
                    else:
                        # Create new promise
                        promise = Promise(
                            title=result['title'],
                            description=result.get('description', ''),
                            source=result.get('source', 'Unknown'),
                            source_url=result.get('source_url', ''),
                            category=result.get('category', 'general'),
                        )
                        update_promise_scores(promise)
                        db.session.add(promise)
                        new_count += 1
                        logger.debug(f"Created new promise: {promise.title[:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing result: {e}", exc_info=True)
                    continue
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"Scrape complete: {new_count} new, {updated_count} updated")
            
            # Emit SocketIO event to notify clients
            socketio.emit('promises_updated', {
                'message': 'New promises available',
                'new_count': new_count,
                'updated_count': updated_count,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in scrape_and_analyze: {e}", exc_info=True)
            db.session.rollback()


def init_scheduler():
    """
    Initialize and start the background scheduler.
    
    Uses safe state checking to avoid multiple scheduler instances.
    NOTE: APScheduler with SQLite has limitations for concurrent access.
    """
    global scheduler
    
    # Check if scheduler already exists and is running
    if scheduler is not None:
        try:
            if scheduler.running:
                logger.info("Scheduler already running, skipping initialization")
                return
        except Exception:
            pass
    
    try:
        scheduler = BackgroundScheduler()
        
        # Schedule scraping every 30 minutes
        scheduler.add_job(
            func=scrape_and_analyze,
            trigger=IntervalTrigger(minutes=30),
            id='scrape_job',
            name='Scrape and analyze promises',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}", exc_info=True)


# Routes

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')


@app.route('/api/promises')
def get_promises():
    """
    API endpoint to get all promises.
    
    Returns:
        JSON array of promise objects
    """
    try:
        promises = Promise.query.order_by(Promise.created_at.desc()).all()
        return jsonify([p.to_dict() for p in promises])
    except Exception as e:
        logger.error(f"Error fetching promises: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch promises'}), 500


@app.route('/api/promises/<int:promise_id>')
def get_promise(promise_id):
    """
    API endpoint to get a single promise by ID.
    
    Args:
        promise_id: Promise ID
    
    Returns:
        JSON promise object or 404
    """
    try:
        promise = Promise.query.get_or_404(promise_id)
        return jsonify(promise.to_dict())
    except Exception as e:
        logger.error(f"Error fetching promise {promise_id}: {e}", exc_info=True)
        return jsonify({'error': 'Promise not found'}), 404


@app.route('/api/scrape/now', methods=['POST'])
def manual_scrape():
    """
    API endpoint to trigger manual scraping.
    
    Returns:
        JSON response with scrape status
    """
    try:
        logger.info("Manual scrape triggered via API")
        
        # Run scrape synchronously (could be made async for better UX)
        scrape_and_analyze()
        
        return jsonify({
            'status': 'success',
            'message': 'Scrape completed successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in manual scrape: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Scrape failed',
            'error': str(e)
        }), 500


# SocketIO events

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
    logger.info(f"Update requested by client: {request.sid}")
    try:
        promises = Promise.query.order_by(Promise.created_at.desc()).limit(10).all()
        emit('promises_update', [p.to_dict() for p in promises])
    except Exception as e:
        logger.error(f"Error sending update: {e}", exc_info=True)


# Application initialization

def create_app():
    """
    Application factory for creating and configuring the Flask app.
    
    Returns:
        Configured Flask app
    """
    with app.app_context():
        # Create database tables
        db.create_all()
        logger.info("Database tables created")
        
        # Initialize scheduler
        init_scheduler()
    
    return app


if __name__ == '__main__':
    """
    Run the application directly.
    
    For production, use a production WSGI server like gunicorn:
        gunicorn -k eventlet -w 1 'mamdani_tracker.app:create_app()'
    """
    logger.info("Starting Mamdani Tracker application")
    
    # Create app and initialize
    create_app()
    
    # Run with SocketIO
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to prevent scheduler duplication
    )
