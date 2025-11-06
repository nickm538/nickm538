"""
Database models for the Mamdani Tracker application.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Promise(db.Model):
    """
    Model representing a political promise to track.
    """
    __tablename__ = 'promises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date_made = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Not Started')
    
    # Analyzer fields
    priority_score = db.Column(db.Float, default=0.0)
    feasibility_score = db.Column(db.Float, default=0.0)
    impact_score = db.Column(db.Float, default=0.0)
    urgency_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Fields for analyzer computation
    budget_required = db.Column(db.Float, default=0.0)  # in millions
    legislative_complexity = db.Column(db.Integer, default=1)  # 1-5 scale
    public_interest = db.Column(db.Integer, default=5)  # 1-10 scale
    deadline_days = db.Column(db.Integer, nullable=True)
    
    # Timestamps (use UTC)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """Convert promise to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'date_made': self.date_made.isoformat() if self.date_made else None,
            'status': self.status,
            'priority_score': round(self.priority_score, 2),
            'feasibility_score': round(self.feasibility_score, 2),
            'impact_score': round(self.impact_score, 2),
            'urgency_score': round(self.urgency_score, 2),
            'overall_score': round(self.overall_score, 2),
            'budget_required': self.budget_required,
            'legislative_complexity': self.legislative_complexity,
            'public_interest': self.public_interest,
            'deadline_days': self.deadline_days,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class NewsArticle(db.Model):
    """
    Model representing scraped news articles related to promises.
    """
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    snippet = db.Column(db.Text, nullable=True)
    published_date = db.Column(db.DateTime, nullable=True)
    
    # Link to promise if relevant
    promise_id = db.Column(db.Integer, db.ForeignKey('promises.id'), nullable=True)
    promise = db.relationship('Promise', backref='related_articles')
    
    # Timestamps (use UTC)
    scraped_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        """Convert article to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'snippet': self.snippet,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'promise_id': self.promise_id,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }
