# app/db/mongo.py
import os
import cv2
import base64
from datetime import datetime
from pymongo import MongoClient

mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017")
mongo_client = MongoClient(mongo_url)
db = mongo_client["yoloapp"]
collection = db["long_presence"]

def clear_snapshots():
    count = collection.count_documents({})
    if count > 0:
        print(f"[MongoDB] Clearing {count} snapshot(s)...")
        collection.delete_many({})
    else:
        print("[MongoDB] No snapshots to clear.")

# Clear the collection automatically on import
clear_snapshots()

def get_recent_snapshots(limit=20):
    """Return recent snapshots from MongoDB"""
    return list(collection.find().sort("timestamp", -1).limit(limit))