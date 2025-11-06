"""
Database models for Mamdani Promise Tracker
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Promise(db.Model):
    """Model for tracking campaign promises"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))  # e.g., Housing, Transportation, Education
    source_url = db.Column(db.String(1000))  # Where the promise was made
    date_made = db.Column(db.DateTime, default=datetime.utcnow)

    # Status tracking
    status = db.Column(db.String(50), default='Not Yet In Office')  # Delivered, Failed, In Progress, Not Discussed, Not Yet In Office
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # AI Analysis
    likelihood_score = db.Column(db.Float, default=0.5)  # 0-1 score
    likelihood_rank = db.Column(db.Integer)  # Overall ranking
    analysis_text = db.Column(db.Text)  # AI-generated analysis

    # Factors for likelihood calculation
    budget_required = db.Column(db.String(50))  # Low, Medium, High, Very High
    legislative_complexity = db.Column(db.String(50))  # Simple, Moderate, Complex
    public_support = db.Column(db.Float)  # 0-1 score
    political_alignment = db.Column(db.Float)  # 0-1 score with current political climate

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    updates = db.relationship('PromiseUpdate', backref='promise', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'source_url': self.source_url,
            'date_made': self.date_made.isoformat() if self.date_made else None,
            'status': self.status,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'likelihood_score': self.likelihood_score,
            'likelihood_rank': self.likelihood_rank,
            'analysis_text': self.analysis_text,
            'budget_required': self.budget_required,
            'legislative_complexity': self.legislative_complexity,
            'public_support': self.public_support,
            'political_alignment': self.political_alignment,
            'updates_count': len(self.updates)
        }


class PromiseUpdate(db.Model):
    """Model for tracking updates/news about promises"""
    id = db.Column(db.Integer, primary_key=True)
    promise_id = db.Column(db.Integer, db.ForeignKey('promise.id'), nullable=False)

    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    source_url = db.Column(db.String(1000))
    source_name = db.Column(db.String(200))  # e.g., "New York Times", "Twitter"

    # Change tracking
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    status_changed = db.Column(db.Boolean, default=False)

    sentiment = db.Column(db.String(20))  # Positive, Negative, Neutral

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notified = db.Column(db.Boolean, default=False)  # Whether push notification was sent

    def to_dict(self):
        return {
            'id': self.id,
            'promise_id': self.promise_id,
            'title': self.title,
            'content': self.content,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'status_changed': self.status_changed,
            'sentiment': self.sentiment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notified': self.notified
        }


class ScrapeLog(db.Model):
    """Model for tracking scraping activity"""
    id = db.Column(db.Integer, primary_key=True)
    scrape_time = db.Column(db.DateTime, default=datetime.utcnow)
    sources_checked = db.Column(db.Integer, default=0)
    updates_found = db.Column(db.Integer, default=0)
    errors = db.Column(db.Text)
    success = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'scrape_time': self.scrape_time.isoformat() if self.scrape_time else None,
            'sources_checked': self.sources_checked,
            'updates_found': self.updates_found,
            'errors': self.errors,
            'success': self.success
        }
