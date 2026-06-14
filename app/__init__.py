from flask import Flask
from config import config

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from app.routes import main_bp, analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)

    return app

