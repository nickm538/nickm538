"""
Mamdani Promise Tracker - Main Flask Application
Enhanced with AI-powered research (Perplexity + Gemini)
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

from models import db, Promise, PromiseUpdate, ScrapeLog
from scraper import PromiseScraper
from analyzer import PromiseAnalyzer

# Import AI modules (with fallback for when APIs aren't configured)
try:
    from daily_research import DailyResearchEngine
    AI_RESEARCH_AVAILABLE = True
except Exception as e:
    print(f"AI Research not available: {e}")
    AI_RESEARCH_AVAILABLE = False

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

# Initialize AI research engine if available
ai_research_engine = None
if AI_RESEARCH_AVAILABLE:
    try:
        ai_research_engine = DailyResearchEngine()
        print("AI Research Engine initialized successfully")
    except Exception as e:
        print(f"Failed to initialize AI Research Engine: {e}")
        AI_RESEARCH_AVAILABLE = False

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
    Based on his actual campaign platform as NYC mayor-elect
    """
    initial_promises = [
        {
            'title': 'Universal Free Public Transit (Fare-Free Subway and Buses)',
            'description': 'Eliminate fares for all NYC subway and bus services, making public transit completely free for all residents. Fund through progressive taxation.',
            'category': 'Transportation',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Massive Public Housing Expansion',
            'description': 'Build 100,000+ units of permanently affordable social housing owned by the city, not subject to market forces.',
            'category': 'Housing',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Implement Comprehensive Rent Control',
            'description': 'Freeze rents at current levels and implement strong rent control measures across all housing types.',
            'category': 'Housing',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Low',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Green New Deal for NYC',
            'description': 'Comprehensive climate action plan including building retrofits, renewable energy, and green jobs program.',
            'category': 'Environment',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'Fully Fund Public Schools',
            'description': 'Ensure all NYC public schools receive full funding with reduced class sizes and increased teacher pay.',
            'category': 'Education',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'High',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Medicare for All NYC (City-Level)',
            'description': 'Establish city-run single-payer healthcare system for all NYC residents.',
            'category': 'Healthcare',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Very High',
            'legislative_complexity': 'Complex'
        },
        {
            'title': 'End Police Brutality and Qualified Immunity',
            'description': 'Reform NYPD policies, end qualified immunity for officers, establish community oversight.',
            'category': 'Public Safety',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Raise Minimum Wage to $25/hour',
            'description': 'Establish $25/hour minimum wage for all workers in NYC.',
            'category': 'Economic Development',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Expand Workers Rights and Union Protections',
            'description': 'Strengthen collective bargaining rights and protect workers organizing unions.',
            'category': 'Economic Development',
            'source_url': 'https://www.zohranfornyc.com/platform',
            'budget_required': 'Low',
            'legislative_complexity': 'Moderate'
        },
        {
            'title': 'Close Rikers Island Immediately',
            'description': 'Accelerate closure of Rikers Island jail complex and reform criminal justice system.',
            'category': 'Public Safety',
            'source_url': 'https://www.zohranfornyc.com/platform',
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


# ============ AI-Powered Daily Research ============
def run_ai_daily_research():
    """
    Run AI-powered daily research using Perplexity + Gemini.
    This is the primary research method - more accurate than scraping.
    """
    if not AI_RESEARCH_AVAILABLE or not ai_research_engine:
        print("AI Research not available, falling back to scraper")
        return scheduled_scrape()
    
    with app.app_context():
        print(f"[{datetime.now()}] Starting AI-powered daily research...")
        
        scrape_log = ScrapeLog()
        
        try:
            # Get all promises as dicts
            promises = Promise.query.all()
            promise_dicts = [{
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'category': p.category,
                'status': p.status
            } for p in promises]
            
            # Run the AI research
            research_results = ai_research_engine.run_daily_research(promise_dicts)
            
            scrape_log.sources_checked = 2  # Perplexity + Gemini
            updates_found = 0
            
            # Process status changes
            for change in research_results.get('status_changes', []):
                promise = Promise.query.get(change['promise_id'])
                if promise:
                    old_status = promise.status
                    new_status = change['new_status']
                    
                    # Create update record
                    update = PromiseUpdate(
                        promise_id=promise.id,
                        title=f"Status Update: {change['promise_title'][:100]}",
                        content=change.get('evidence', ''),
                        source_url=research_results.get('daily_news', {}).get('citations', [''])[0] if research_results.get('daily_news', {}).get('citations') else '',
                        source_name='AI Research (Perplexity + Gemini)',
                        old_status=old_status,
                        new_status=new_status,
                        status_changed=True,
                        sentiment='Positive' if new_status in ['Delivered', 'In Progress'] else 'Neutral'
                    )
                    
                    db.session.add(update)
                    updates_found += 1
                    
                    # Update promise status
                    promise.status = new_status
                    promise.last_updated = datetime.utcnow()
                    
                    # Send WebSocket notification
                    socketio.emit('promise_update', {
                        'promise': promise.to_dict(),
                        'update': update.to_dict(),
                        'message': f'Status changed: {old_status} → {new_status}'
                    })
                    
                    update.notified = True
            
            # Process stance changes
            for stance_change in research_results.get('stance_changes_detected', []):
                promise = Promise.query.get(stance_change['promise_id'])
                if promise:
                    update = PromiseUpdate(
                        promise_id=promise.id,
                        title=f"Stance Change Detected: {stance_change['promise_title'][:100]}",
                        content=stance_change.get('details', ''),
                        source_url='',
                        source_name='AI Research (Perplexity + Gemini)',
                        old_status=promise.status,
                        new_status='Stance Changed',
                        status_changed=True,
                        sentiment='Neutral'
                    )
                    
                    db.session.add(update)
                    updates_found += 1
                    
                    # Notify about stance change
                    socketio.emit('stance_change', {
                        'promise': promise.to_dict(),
                        'details': stance_change.get('details', ''),
                        'message': f'Stance change detected for: {promise.title}'
                    })
            
            # Process general updates (no status change but relevant news)
            for promise_update in research_results.get('promise_updates', []):
                if promise_update.get('promise_id') not in [c['promise_id'] for c in research_results.get('status_changes', [])]:
                    # Only add if not already added as status change
                    if promise_update.get('relevance_score', 0) > 0.7:
                        promise = Promise.query.get(promise_update['promise_id'])
                        if promise:
                            # Check if similar update already exists
                            existing = PromiseUpdate.query.filter_by(
                                promise_id=promise.id
                            ).filter(
                                PromiseUpdate.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
                            ).first()
                            
                            if not existing:
                                update = PromiseUpdate(
                                    promise_id=promise.id,
                                    title=f"News Update: {promise_update['promise_title'][:100]}",
                                    content=promise_update.get('evidence', ''),
                                    source_url=promise_update.get('citations', [''])[0] if promise_update.get('citations') else '',
                                    source_name='AI Research (Perplexity + Gemini)',
                                    old_status=promise.status,
                                    new_status=promise.status,
                                    status_changed=False,
                                    sentiment='Neutral'
                                )
                                
                                db.session.add(update)
                                updates_found += 1
            
            db.session.commit()
            
            scrape_log.updates_found = updates_found
            scrape_log.success = True
            scrape_log.errors = research_results.get('summary', '')
            
            print(f"AI Research completed: {updates_found} updates processed")
            
        except Exception as e:
            print(f"Error during AI research: {e}")
            import traceback
            traceback.print_exc()
            scrape_log.success = False
            scrape_log.errors = str(e)
            db.session.rollback()
        
        finally:
            db.session.add(scrape_log)
            db.session.commit()


# ============ Legacy Scheduled Scraping (Fallback) ============
def scheduled_scrape():
    """
    Run scheduled scrape of all sources (legacy method).
    Used as fallback when AI research is not available.
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
        'last_scrape': last_scrape.to_dict() if last_scrape else None,
        'ai_research_available': AI_RESEARCH_AVAILABLE
    })


@app.route('/api/scrape/now', methods=['POST'])
def trigger_scrape():
    """Manually trigger a research scan"""
    try:
        if AI_RESEARCH_AVAILABLE:
            run_ai_daily_research()
            return jsonify({'success': True, 'message': 'AI Research completed', 'method': 'ai'})
        else:
            scheduled_scrape()
            return jsonify({'success': True, 'message': 'Scrape completed', 'method': 'scraper'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/research/promise/<int:promise_id>', methods=['POST'])
def research_single_promise(promise_id):
    """Run focused AI research on a single promise"""
    if not AI_RESEARCH_AVAILABLE:
        return jsonify({'success': False, 'error': 'AI Research not available'}), 503
    
    promise = Promise.query.get_or_404(promise_id)
    
    try:
        result = ai_research_engine.research_single_promise({
            'id': promise.id,
            'title': promise.title,
            'description': promise.description,
            'category': promise.category,
            'status': promise.status
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ WebSocket Events ============
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to Mamdani Promise Tracker', 'ai_available': AI_RESEARCH_AVAILABLE})


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
        # Schedule AI research daily at 6 AM, 12 PM, and 6 PM
        if AI_RESEARCH_AVAILABLE:
            scheduler.add_job(
                func=run_ai_daily_research,
                trigger='cron',
                hour='6,12,18',
                id='ai_daily_research',
                name='AI-powered daily research',
                replace_existing=True
            )
            print("Scheduler started - AI research at 6 AM, 12 PM, and 6 PM")
        else:
            # Fallback to legacy scraping every 6 hours
            scheduler.add_job(
                func=scheduled_scrape,
                trigger='interval',
                hours=6,
                id='promise_scraper',
                name='Scrape news sources for promise updates',
                replace_existing=True
            )
            print("Scheduler started - scraping every 6 hours (AI not available)")

        scheduler.start()


if __name__ == '__main__':
    # Initialize database
    init_database()

    # Start background scheduler
    start_scheduler()

    # Run the app
    print("Starting Mamdani Promise Tracker...")
    print(f"AI Research: {'ENABLED' if AI_RESEARCH_AVAILABLE else 'DISABLED'}")
    print("Dashboard available at: http://localhost:5000")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
