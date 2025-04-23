import cv2
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from db.mongo import get_recent_snapshots
import requests
import numpy as np

router = APIRouter()
YOLO_ENGINE_URL = "http://yolo:5000/detect"
YOLO_ENGINE_STATS_URL = "http://yolo:5000/stats"

# @router.post("/video_feed")
def analyze_video():
    cap = cv2.VideoCapture("recordings/Sales hall 2.mp4")
    if not cap.isOpened():
        return JSONResponse(status_code=400, content={"error": "Unable to read video"})

    while True:
        ret, frame = cap.read()
        frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if not ret:
            print("Done processing video.")
            break
        width, height = int(frame.shape[1]/2), int(frame.shape[0]/2)
        frame = cv2.resize(frame, (width, height))  # Resize frame to 640x360
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}

        try:
            response = requests.post(YOLO_ENGINE_URL, files=files, timeout=5)
            if response.status_code == 200:
                img_np = np.frombuffer(response.content, np.uint8)
                result_bytes = img_np.tobytes()
            else:
                print(f"Failed on frame {frame_count}: {response.status_code} {response.text}")
                result_bytes = img_encoded.tobytes()
        except requests.RequestException as e:
            print(f"Exception on frame {frame_count}: {e}")
            result_bytes = img_encoded.tobytes()
        # Stream as MJPEG
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + result_bytes + b"\r\n"
        )
    cap.release()

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(analyze_video(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


# Get objects stats from engine state
@router.get("/stats")
def get_engine_stats():
    try:
        response = requests.get(YOLO_ENGINE_STATS_URL, timeout=5)
        response = response.json()
        object_stats = response.get("stats", {})
        active_ids = response.get("live_ids", [])
        return JSONResponse({
        "count": len(active_ids),
        "objects": [
            {
                "id": obj_id,
                "lifetime": round(object_stats[obj_id]["lifetime"], 2)
            }
            for obj_id in active_ids
        ]
    })
    except requests.exceptions.RequestException as e:
        pass



@router.get("/snapshot_data", response_class=JSONResponse)
def get_snapshot_data():
    snapshots = get_recent_snapshots(limit=10)
    data = [
        {
            "track_id": snap["track_id"],
            "image_base64": snap["image_base64"],
        }
        for snap in snapshots
    ]
    return data