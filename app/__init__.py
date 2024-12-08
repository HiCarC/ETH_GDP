from flask import Flask
from flask_caching import Cache
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config

cache = Cache()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    cache.init_app(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Start scheduler
    scheduler.start()
    
    return app 