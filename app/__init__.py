from flask import Flask
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
})

def create_app():
    app = Flask(__name__)
    cache.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app

app = create_app() 