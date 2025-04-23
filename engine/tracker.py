# app/engine/tracker.py
import cv2
import time
import torch
import torchvision.ops as ops
from deep_sort_realtime.deepsort_tracker import DeepSort

class deepSortTracker:
    def __init__(self):
        # Initialize tracker
        self.tracker = DeepSort(max_age=30)  # controls how long to keep lost tracks
        
        # Stats and alerts configs
        self.alert_threshold = 120  # seconds (2 minutes for testing)
        self.object_stats = {}
        self.live_ids = []

        # Define your custom box (door region) [x1, y1, x2, y2]
        self.door_box = None # Adjust as needed
        self.iou_thresh = 0.05  # IoU threshold for rejecting detections overlapping with the door
        self.raise_alert = False
        
    def filter_door_detections(self, frame, detections):
        # Set door box if not set        
        x1, y1, x2, y2 = int(frame.shape[1]*0.5), 10, int(frame.shape[1]*0.5) + 80, 100
        if self.door_box is None:
            self.door_box = torch.tensor([[x1, y1, x2, y2]], dtype=torch.float32)
        # Draw box on door 
        # x1, y1, x2, y2 = map(int, self.door_box[0].tolist())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 1)
        cv2.putText(frame, f"Door", (x1, (y1 - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 2)
        # Check if any detection overlaps with the door box (Compute IoU with door region)
        boxes = detections[:, :4]  # Get the bounding boxes
        ious = ops.box_iou(boxes, self.door_box).squeeze()
        keep = ious < self.iou_thresh  # Keep detections with low IoU

        return detections[keep].cpu().numpy()

    def update_track_stats(self, track, current_time):
        # Record entry time
        track_id = track.track_id
        if track_id not in self.object_stats:
            self.object_stats[track_id] = {'entered_at': current_time, 'last_seen': current_time}
        else:
            self.object_stats[track_id]['last_seen'] = current_time
        # Calculate lifetime
        lifetime = self.object_stats[track_id]['last_seen'] - self.object_stats[track_id]['entered_at']
        self.object_stats[track_id]['lifetime'] = lifetime
        # Check if lifetime exceeds threshold, take an action (e.g., send alert)
        alert = True if lifetime > self.alert_threshold else False
        self.object_stats[track_id]['alert'] = alert
        if alert:    # Store snapshot in stats
            self.raise_alert = True
            self.object_stats[track.track_id]['snapshot_pts'] = track.to_ltrb()
        return lifetime

    def draw_detection(self, frame, track, lifetime):
        # Draw detection on the frame
        l, t, w, h = map(int, track.to_ltrb())
        cv2.rectangle(frame, (l, t), (w, h), (0, 255, 0), 1)
        cv2.putText(frame, f"ID {track.track_id}", (l, t - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.putText(frame, f"Time: {lifetime:.1f}s", (l, t - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
    def color_alert_frame(self, frame):
        # Overlay a red color on the frame
        overlay = frame.copy()
        overlay[:] = (0, 0, 255)  # Red color
        alpha = 0.3  # Transparency factor
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0,dst=frame)

    def update(self, frame, objects):
        filtered_detections = self.filter_door_detections(frame, objects.xyxy[0])
        yolo_detections = [] # Format: [x1, y1, x2, y2, confidence, class_id]
        for det in filtered_detections:
            x1, y1, x2, y2, conf, class_id = det.squeeze()
            yolo_detections.append(([x1, y1, x2 - x1, y2 - y1], conf, 'person'))

        tracks = self.tracker.update_tracks(yolo_detections, frame=frame)
        now = time.time()
        self.live_ids = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            self.live_ids.append(track.track_id)
            # Update track stats
            lifetime = self.update_track_stats(track, now)
            # Draw detection
            self.draw_detection(frame, track, lifetime)
        if self.raise_alert:
            self.color_alert_frame(frame)
            self.raise_alert = False
        return frame
    
    def get_objects_stats(self):
        return self.object_stats
    
