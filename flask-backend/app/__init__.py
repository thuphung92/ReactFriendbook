from flask import Flask
from config import Config
from flask_login import LoginManager #for logging users in and maintaining a session
from flask_sqlalchemy import SQLAlchemy #this talk to our database for us
from flask_migrate import Migrate #Makes altering the Database a lot easier
from flask_moment import Moment
from flask_cors import CORS

# init Login Manager
login = LoginManager()
#where to be sent if you are not logged in
login.login_view = 'auth.login'
login.login_message = "You must be logged in to view the page"
login.login_message_category = "warning"
# init the database from_object
db = SQLAlchemy()
# init Migrate
migrate = Migrate()
moment = Moment()
cors= CORS()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)

    cors.init_app(app)

    from .blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from .blueprints.api import bp as api_bp
    app.register_blueprint(api_bp)

    from .blueprints.social import bp as social_bp
    app.register_blueprint(social_bp)

    return app