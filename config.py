import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ProductionConfig(Config):
    DEBUG = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class TestingConfig(Config):
    TESTING = True
    GEMINI_API_KEY = "test-key"

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

