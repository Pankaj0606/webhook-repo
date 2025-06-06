import os

class Config:
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
