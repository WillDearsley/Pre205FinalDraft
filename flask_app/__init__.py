import os
from flask import Flask
from flask_assets import Bundle, Environment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy()
# Initialize Flask-Login
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from flask_app.models import Users
    return Users.query.get(int(user_id))

def create_app():
    app = Flask(__name__)

    # Configure PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/mydatabase')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = "THE_BOYS_SECRET"

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    # Initialize Flask-Login with the app
    login_manager.init_app(app)
    login_manager.login_view = 'api.loginendpoint'  # Specify the login view

    # Initialize Flask-Assets
    assets = Environment(app)
    css = Bundle("src/main.css", output="dist/main.css")
    js = Bundle("src/*.js", output="dist/main.js")

    # lets register our main and app routes
    from flask_app.main.routes import main
    from flask_app.api.routes import api

    app.register_blueprint(main)
    app.register_blueprint(api)

    # Register assets
    assets.register("css", css)
    assets.register("js", js)
    css.build()
    js.build()

    # Create database tables (if they don't exist)
    with app.app_context():
        # uncomment the following line if you want to restart the db from scratch
        #db.drop_all()
        db.create_all()

    return app
