import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

if os.getenv("ENV", "local").lower() != "production":
    load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# Windows par 'TLSV1_ALERT_INTERNAL_ERROR' ka fix:
# MongoClient ko certifi ka CA bundle explicitly do.
client = MongoClient(
    MONGO_URL,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000,
    connectTimeoutMS=20000,
)

db = client["knowledgeos"]