from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    """User model for storing user account information"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    campaigns = db.relationship('OffChainCampaign', backref='creator', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.wallet_address}>'


class OffChainCampaign(db.Model):
    """
    Campaign model for storing off-chain campaign information
    This complements the on-chain campaign data to store additional metadata
    """
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    chain_id = db.Column(db.Integer, nullable=False)  # Blockchain campaign ID
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(255))  # Comma-separated tags
    website = db.Column(db.String(255))
    social_links = db.Column(db.Text)  # JSON string of social media links
    updates = db.Column(db.Text)  # JSON string of campaign updates
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='campaign', lazy='dynamic')

    def __repr__(self):
        return f'<Campaign {self.title}>'


class Comment(db.Model):
    """Comment model for storing user comments on campaigns"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Comment {self.id}>'


class UserActivity(db.Model):
    """UserActivity model for tracking user activities"""
    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # e.g., 'contribution', 'campaign_creation', 'comment'
    campaign_id = db.Column(db.Integer)  # References chain_id from blockchain
    activity_data = db.Column(db.Text)  # JSON string with activity-specific data (renamed from metadata)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<UserActivity {self.activity_type}>'


class Contribution(db.Model):
    """
    Contribution model for storing contribution records 
    (mirror of blockchain data for faster querying)
    """
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, nullable=False)  # References chain_id from blockchain
    contributor_address = db.Column(db.String(42), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in ETH
    transaction_hash = db.Column(db.String(66), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<Contribution {self.transaction_hash}>'