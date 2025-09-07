from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Configure CORS to allow requests from your Shopify domains
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://www.hemlockandoak.com",
                "https://hemlock-oak.myshopify.com",
                "http://localhost:3000",
                "http://127.0.0.1:9292",
                "http://localhost:9292"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
