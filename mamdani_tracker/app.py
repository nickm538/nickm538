"""
Mamdani Promise Tracker - Main Flask Application
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

from models import db, Promise, PromiseUpdate, ScrapeLog
from scraper import PromiseScraper
from analyzer import PromiseAnalyzer

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mamdani_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
scraper = PromiseScraper()
analyzer = PromiseAnalyzer()

# Background scheduler
scheduler = BackgroundScheduler()


# ============ Database Initialization ============
def init_database():
    """Initialize database with tables and seed data"""
    with app.app_context():
        db.create_all()

        # Check if we need to seed initial promises
        if Promise.query.count() == 0:
            print("Seeding initial promises...")
            seed_initial_promises()


def seed_initial_promises():
    """
    Seed database with known Mamdani campaign promises
    This is based on his campaign platform as NYC mayor-elect
    """
    initial_promises = [
        {
            'title': 'Universal Free Public Transit (Fare-Free Subway and Buses)',
            'description': 'Eliminate fares for all NYC subway and bus services, making public transit completely free for all residents. Fund through progressive taxation.',
            'category': 'Transportation',
            'source_url': 'https://example.com/campaign',  # Replace with actual source
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Massive Public Housing Expansion',
            'description': 'Build 100,000+ units of permanently affordable social housing owned by the city, not subject to market forces.',
            'category': 'Housing',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Implement Comprehensive Rent Control',
            'description': 'Freeze rents at current levels and implement strong rent control measures across all housing types.',
            'category': 'Housing',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Low',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Green New Deal for NYC',
            'description': 'Comprehensive climate action plan including building retrofits, renewable energy, and green jobs program.',
            'category': 'Environment',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Fully Fund Public Schools',
            'description': 'Ensure all NYC public schools receive full funding with reduced class sizes and increased teacher pay.',
            'category': 'Education',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'High',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Medicare for All NYC (City-Level)',
            'description': 'Establish city-run single-payer healthcare system for all NYC residents.',
            'category': 'Healthcare',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'End Police Brutality and Qualified Immunity',
            'description': 'Reform NYPD policies, end qualified immunity for officers, establish community oversight.',
            'category': 'Public Safety',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Raise Minimum Wage to $25/hour',
            'description': 'Establish $25/hour minimum wage for all workers in NYC.',
            'category': 'Economic Development',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Expand Workers Rights and Union Protections',
            'description': 'Strengthen collective bargaining rights and protect workers organizing unions.',
            'category': 'Economic Development',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Close Rikers Island Immediately',
            'description': 'Accelerate closure of Rikers Island jail complex and reform criminal justice system.',
            'category': 'Public Safety',
            'source_url': 'https://example.com/campaign',
            'budget_required': 'High',
            'legislative_complexity': 'Complex'
        }
    ]

    for promise_data in initial_promises:
        promise = Promise(**promise_data)

        # Run AI analysis on the promise
        analysis = analyzer.analyze_promise(promise)
        promise.likelihood_score = analysis['likelihood_score']
        promise.analysis_text = analysis['analysis_text']

        db.session.add(promise)

    db.session.commit()

    # Rank all promises
    promises = Promise.query.all()
    analyzer.rank_all_promises(promises)
    db.session.commit()

    print(f"Seeded {len(initial_promises)} initial promises")


# ============ Scheduled Scraping ============
def scheduled_scrape():
    """
    Run scheduled scrape of all sources
    This runs every 6 hours
    """
    with app.app_context():
        print(f"[{datetime.now()}] Starting scheduled scrape...")

        scrape_log = ScrapeLog()

        try:
            # Get all articles
            articles, sources_checked = scraper.scrape_all_sources()
            scrape_log.sources_checked = sources_checked

            print(f"Found {len(articles)} articles from {sources_checked} sources")

            # Get all promises
            promises = Promise.query.all()
            updates_found = 0

            # Check each article against each promise
            for promise in promises:
                for article in articles:
                    analysis = scraper.analyze_article_for_promise_update(article, promise)

                    if analysis['relevant']:
                        # Check if this update already exists
                        existing = PromiseUpdate.query.filter_by(
                            promise_id=promise.id,
                            source_url=article['url']
                        ).first()

                        if not existing:
                            # Create new update
                            old_status = promise.status
                            new_status = analysis.get('status_change') or promise.status

                            update = PromiseUpdate(
                                promise_id=promise.id,
                                title=analysis['title'],
                                content=analysis.get('summary', ''),
                                source_url=analysis['url'],
                                source_name=analysis['source'],
                                old_status=old_status,
                                new_status=new_status,
                                status_changed=(old_status != new_status),
                                sentiment=analysis['sentiment']
                            )

                            db.session.add(update)
                            updates_found += 1

                            # Update promise status if changed
                            if update.status_changed:
                                promise.status = new_status
                                promise.last_updated = datetime.utcnow()

                                # Send push notification via WebSocket
                                socketio.emit('promise_update', {
                                    'promise': promise.to_dict(),
                                    'update': update.to_dict(),
                                    'message': f'Status changed: {old_status} → {new_status}'
                                })

                                update.notified = True

            db.session.commit()
            scrape_log.updates_found = updates_found
            scrape_log.success = True

            print(f"Scrape completed: {updates_found} new updates found")

        except Exception as e:
            print(f"Error during scrape: {e}")
            scrape_log.success = False
            scrape_log.errors = str(e)
            db.session.rollback()

        finally:
            db.session.add(scrape_log)
            db.session.commit()


# ============ Routes ============
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/promises')
def get_promises():
    """Get all promises with their current status"""
    category = request.args.get('category')
    status = request.args.get('status')
    sort_by = request.args.get('sort', 'rank')  # rank, date, likelihood

    query = Promise.query

    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)

    if sort_by == 'rank':
        query = query.order_by(Promise.likelihood_rank.asc())
    elif sort_by == 'date':
        query = query.order_by(Promise.date_made.desc())
    elif sort_by == 'likelihood':
        query = query.order_by(Promise.likelihood_score.desc())

    promises = query.all()

    return jsonify({
        'promises': [p.to_dict() for p in promises],
        'total': len(promises)
    })


@app.route('/api/promises/<int:promise_id>')
def get_promise(promise_id):
    """Get detailed information about a specific promise"""
    promise = Promise.query.get_or_404(promise_id)
    updates = PromiseUpdate.query.filter_by(promise_id=promise_id).order_by(
        PromiseUpdate.created_at.desc()
    ).all()

    return jsonify({
        'promise': promise.to_dict(),
        'updates': [u.to_dict() for u in updates]
    })


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    total_promises = Promise.query.count()

    status_counts = db.session.query(
        Promise.status,
        db.func.count(Promise.id)
    ).group_by(Promise.status).all()

    category_counts = db.session.query(
        Promise.category,
        db.func.count(Promise.id)
    ).group_by(Promise.category).all()

    avg_likelihood = db.session.query(
        db.func.avg(Promise.likelihood_score)
    ).scalar() or 0

    last_scrape = ScrapeLog.query.order_by(
        ScrapeLog.scrape_time.desc()
    ).first()

    return jsonify({
        'total_promises': total_promises,
        'status_breakdown': {status: count for status, count in status_counts},
        'category_breakdown': {cat: count for cat, count in category_counts},
        'average_likelihood': round(avg_likelihood, 2),
        'last_scrape': last_scrape.to_dict() if last_scrape else None
    })


@app.route('/api/scrape/now', methods=['POST'])
def trigger_scrape():
    """Manually trigger a scrape (for testing)"""
    try:
        scheduled_scrape()
        return jsonify({'success': True, 'message': 'Scrape completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ WebSocket Events ============
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Mamdani Promise Tracker'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Client requests current data"""
    promises = Promise.query.order_by(Promise.likelihood_rank.asc()).all()
    emit('promises_data', {
        'promises': [p.to_dict() for p in promises]
    })


# ============ Application Startup ============
def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Schedule scraping every 6 hours
        scheduler.add_job(
            func=scheduled_scrape,
            trigger='interval',
            hours=6,
            id='promise_scraper',
            name='Scrape news sources for promise updates',
            replace_existing=True
        )

        scheduler.start()
        print("Scheduler started - scraping every 6 hours")


if __name__ == '__main__':
    # Initialize database
    init_database()

    # Start background scheduler
    start_scheduler()

    # Run the app
    print("Starting Mamdani Promise Tracker...")
    print("Dashboard available at: http://localhost:5000")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
