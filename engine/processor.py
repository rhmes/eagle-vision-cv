# engine/cv_handler.py
from model import yoloHandler
from tracker import deepSortTracker
from db.postgres import insert_tracking_record
from db.mongo import insert_user_snapshot

class processor:
    def __init__(self):
        self.detector = yoloHandler()
        self.tracker = deepSortTracker()  # controls how long to keep lost tracks
    
    def _update_stats_db(self, track_id, entered_at, last_seen):
        insert_tracking_record(track_id, entered_at, last_seen)

    def _update_alerts_db(self, track_id, crop_image):
       insert_user_snapshot(track_id, crop_image)

    def _db_handler(self, frame):
        active_ids = self.get_live_ids()
        stats = self.get_stats()
        for track_id in active_ids:
            entered_at = stats[track_id]['entered_at']
            last_seen = stats[track_id]['last_seen']
            alert = stats[track_id]['alert']
            # Push stats to DB
            self._update_stats_db(track_id, entered_at, last_seen)
            # Push alerts to DB
            if alert:
                pts = stats[track_id]['snapshot_pts']
                l, t, w, h = map(int, pts)
                crop_image = frame[t:h, l:w]
                self._update_alerts_db(track_id, crop_image)
                stats[track_id]['snapshot_pts'] = []

    def get_stats(self):
        return self.tracker.get_objects_stats()
    
    def get_live_ids(self):
        return self.tracker.live_ids

    def process_frame(self, frame):
        objects = self.detector.process_frame(frame)
        processed_frame = self.tracker.update(frame.copy(), objects)
        self._db_handler(frame)
        return processed_frame
    