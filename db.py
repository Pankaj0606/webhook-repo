from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

mongo_uri = os.getenv("MONGO_URI")
mongo_db = os.getenv("MONGO_DB", "github_webhooks")  # Default fallback

client = MongoClient(mongo_uri)
db = client[mongo_db]
events = db.events
