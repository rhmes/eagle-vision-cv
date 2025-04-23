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

def insert_user_snapshot(track_id: int, crop_image):
# Validate image
    if crop_image is None or crop_image.size == 0:
        print(f"[WARN] Empty or invalid crop for track_id={track_id}")
        return

    # Encode image to JPEG
    success, buffer = cv2.imencode('.jpg', crop_image)
    if not success:
        print(f"[ERROR] Failed to encode image for track_id={track_id}")
        return

    # Convert JPEG buffer to base64 string
    img_str = base64.b64encode(buffer).decode("utf-8")

    # Avoid duplicates
    if collection.find_one({"track_id": track_id}):
        return

    # Create and insert the document
    doc = {
        "track_id": track_id,
        "timestamp": datetime.now(),
        "image_base64": img_str
    }

    try:
        collection.insert_one(doc)
        print(f"[INFO] Inserted snapshot for track_id={track_id}")
    except Exception as e:
        print(f"[ERROR] Failed to insert MongoDB doc: {e}")

def get_recent_snapshots(limit=20):
    """Return recent snapshots from MongoDB"""
    return list(collection.find().sort("timestamp", -1).limit(limit))