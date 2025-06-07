from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def init_app_db(app):
    """Initializes the database with the Flask app."""
    db.init_app(app)

class UserSession(db.Model):
    __tablename__ = 'user_session'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    consent_agreed = db.Column(db.Boolean, default=False)
    assessment_summary_text = db.Column(db.Text, nullable=True) # Store final summary

    responses = db.relationship('Response', backref='user_session', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<UserSession {self.id}>'

class Response(db.Model):
    __tablename__ = 'response'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_session_id = db.Column(db.String(36), db.ForeignKey('user_session.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    answer_text = db.Column(db.String(200), nullable=False)
    answer_value = db.Column(db.Integer, nullable=True) # Numerical value for scoring
    category = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Response {self.question_id}: {self.answer_text[:20]}>'