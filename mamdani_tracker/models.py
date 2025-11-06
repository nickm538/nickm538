"""
Database models for the Mamdani Tracker application.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Promise(db.Model):
    """Model representing a political promise."""
    
    __tablename__ = 'promises'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(100))
    source_url = db.Column(db.String(1000))
    category = db.Column(db.String(100))
    
    # Scoring fields
    feasibility_score = db.Column(db.Float, default=0.5)
    impact_score = db.Column(db.Float, default=0.5)
    priority_score = db.Column(db.Float, default=0.5)
    budget_required = db.Column(db.Float, default=0.0)
    legislative_complexity = db.Column(db.Float, default=0.5)
    
    # Timestamps (UTC)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def to_dict(self):
        """Convert promise to dictionary for API responses."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'source_url': self.source_url,
            'category': self.category,
            'feasibility_score': self.feasibility_score,
            'impact_score': self.impact_score,
            'priority_score': self.priority_score,
            'budget_required': self.budget_required,
            'legislative_complexity': self.legislative_complexity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Promise {self.id}: {self.title[:50]}>'
