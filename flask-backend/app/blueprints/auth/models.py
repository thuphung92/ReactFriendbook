from app import db
from flask_login import UserMixin
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    token = token = db.Column(db.String, index=True, unique=True)
    token_exp = token_exp = db.Column(db.DateTime)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    # token methods start
    def generate_token(self):
        self.token = secrets.token_urlsafe(32)
        self.save()
        return self.token

    def get_token(self, exp=2592000): # will be expired after 30 days
        current_time = dt.utcnow()
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_urlsafe(32)
        self.token_exp=current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() + timedelta(seconds = 61)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_exp < dt.utcnow():
            return None
        return user
    # token methods end

    ### Social Methods Start ###
    def self_posts(self):
        from app.blueprints.social.models import Post
        return Post.query.filter_by(user_id=self.id).order_by(Post.created_on.desc())

    ### Social Methods Ends ###

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'

    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    def check_hashed_password(self, login_password):
        return check_password_hash(self.password,login_password)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = self.hash_password(data['password'])
        self.token = secrets.token_urlsafe(32)
        self.token_exp = dt.utcnow() + timedelta(seconds = 2592000)
        self.save()
    

    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))