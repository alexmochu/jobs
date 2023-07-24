import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from flask import current_app
import jwt
from time import time

from . import db

class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(500), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updateed_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_id = db.Column(db.String(128))
    github_id = db.Column(db.String(128))
    linkedin_id = db.Column(db.String(64), nullable=True, unique=True)
    verified = db.Column(db.String(50))

    def __repr__(self):
        return str(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_username(self):
        return str(self.username)
    
    def get_token(self, expires_in=6000000000000000000):
        return jwt.encode(
            {'username': str(self.username), 'id': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')
        
    
    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['id']
        except:
            return
        user = User.query.get(id)
        return str(user)
    
    def generate_password_reset_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id},
            current_app.config['SECRET_KEY'], algorithm='HS256')
        

    @staticmethod
    def verify_password_reset_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    
class Job(db.Model):
    """
    Create Job Item
    """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(128))
    job_company = db.Column(db.String(128))
    job_location = db.Column(db.String(50))
    job_description = db.Column(db.String(500))
    job_owner = db.Column(db.String, db.ForeignKey('users.username'))
    job_url = db.Column(db.String(128))
    job_type = db.Column(db.String(50))
    application_state = db.Column(db.String(50))
    #business_category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE', onupdate='CASCADE'))

    def save(self):
        """
        Save a job to the database
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Deletes a given job
        """
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        """
        Return a representation of a job instance
        """
        return "<Job: {}>".format(self.job_title)
    
class BlacklistToken(db.Model):
    """
    Token Model for storing blacklisted JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)

    def __init__(self, token):
        self.token = token

    def save(self):
        """Save token"""
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)