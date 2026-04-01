"""
fall_tracker.py
Centroid-based tracker with ego-motion compensation.
Tracks moving blobs by position (class-agnostic) and detects downward falls.
"""

import cv2
import numpy as np
import logging
import time
import config

logger = logging.getLogger(__name__)


class FallTracker:
    """
    Tracks moving blobs by centroid and detects falls via vertical velocity.
    Uses optical flow to estimate camera ego-motion so helmet movement
    doesn't trigger false alerts.
    """

    def __init__(self):
        self.next_id = 0
        self.objects = {}  # id -> {cx, cy, fall_count, missed, rect, trail}
        self.last_alert_time = 0

        # Optical flow state for ego-motion estimation
        self.prev_gray = None
        self.lk_params = dict(
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01)
        )
        self.feature_params = dict(
            maxCorners=200,
            qualityLevel=0.01,
            minDistance=30,
            blockSize=7
        )

        logger.info("Fall Tracker initialized (centroid + ego-motion)")

    def estimate_ego_motion(self, gray):
        """
        Estimate vertical camera motion using sparse optical flow.
        Returns (ego_motion_y, camera_is_moving).
        """
        ego_motion_y = 0.0
        camera_is_moving = False

        if self.prev_gray is not None:
            prev_pts = cv2.goodFeaturesToTrack(self.prev_gray, **self.feature_params)

            if prev_pts is not None and len(prev_pts) > 10:
                next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                    self.prev_gray, gray, prev_pts, None, **self.lk_params
                )
                if next_pts is not None:
                    good_mask = status.flatten() == 1
                    good_prev = prev_pts[good_mask]
                    good_next = next_pts[good_mask]

                    if len(good_prev) > 5:
                        flow = good_next - good_prev
                        flow_y = flow[:, 0, 1]
                        ego_motion_y = float(np.median(flow_y))

                        flow_std = float(np.std(flow_y))
                        if flow_std < 8.0 and abs(ego_motion_y) > 3.0:
                            camera_is_moving = True

        self.prev_gray = gray.copy()
        return ego_motion_y, camera_is_moving

    def update(self, contours, current_time, ego_motion_y=0.0):
        """
        Match new contour centroids to tracked objects and check for falls.

        Args:
            contours: list of cv2 contours (already area-filtered)
            current_time: time.time()
            ego_motion_y: estimated vertical camera motion (subtracted from velocity)

        Returns:
            (fall_detected, tracked_objects_dict)
        """
        fall_detected = False
        velocity_threshold = config.FALL_VELOCITY_THRESHOLD
        min_frames = config.MIN_CONSECUTIVE_FRAMES
        max_dist = config.MAX_TRACKING_DISTANCE
        max_missed = config.MAX_MISSED_FRAMES

        # Extract centroids from contours
        input_centroids = []
        input_rects = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2
            input_centroids.append((cx, cy))
            input_rects.append((x, y, w, h))

        # No detections — increment missed counters
        if len(input_centroids) == 0:
            for obj_id in list(self.objects.keys()):
                self.objects[obj_id]['missed'] += 1
                if self.objects[obj_id]['missed'] > max_missed:
                    del self.objects[obj_id]
            return fall_detected, self.objects

        # No existing objects — register all
        if len(self.objects) == 0:
            for i, (cx, cy) in enumerate(input_centroids):
                self._register(cx, cy, input_rects[i])
            return fall_detected, self.objects

        # Greedy nearest-neighbour matching
        obj_ids = list(self.objects.keys())
        obj_centroids = [(self.objects[oid]['cx'], self.objects[oid]['cy']) for oid in obj_ids]

        used_inputs = set()
        used_objects = set()

        matches = []
        for i, (ocx, ocy) in enumerate(obj_centroids):
            best_dist = float('inf')
            best_j = -1
            for j, (icx, icy) in enumerate(input_centroids):
                dist = np.sqrt((ocx - icx) ** 2 + (ocy - icy) ** 2)
                if dist < best_dist:
                    best_dist = dist
                    best_j = j
            if best_dist < max_dist:
                matches.append((i, best_j, best_dist))

        matches.sort(key=lambda x: x[2])

        for obj_idx, inp_idx, dist in matches:
            if obj_idx in used_objects or inp_idx in used_inputs:
                continue

            obj_id = obj_ids[obj_idx]
            new_cx, new_cy = input_centroids[inp_idx]
            old_cy = self.objects[obj_id]['cy']

            # Vertical velocity compensated for camera motion
            raw_velocity = new_cy - old_cy
            velocity = raw_velocity - ego_motion_y

            if config.DEBUG_MODE:
                logger.debug(
                    f"Object #{obj_id}: raw_vel={raw_velocity:.1f}, "
                    f"ego={ego_motion_y:.1f}, adj_vel={velocity:.1f}"
                )

            # Check for downward fall
            if velocity > velocity_threshold:
                self.objects[obj_id]['fall_count'] += 1
                if self.objects[obj_id]['fall_count'] >= min_frames:
                    if (current_time - self.last_alert_time) > config.ALERT_COOLDOWN:
                        fall_detected = True
                        self.last_alert_time = current_time
                        logger.warning(f"FALL DETECTED - Object #{obj_id}")
                    self.objects[obj_id]['fall_count'] = 0
            elif velocity < -2:  # Moving upward — decay counter
                self.objects[obj_id]['fall_count'] = max(
                    0, self.objects[obj_id]['fall_count'] - 1
                )

            # Update position
            self.objects[obj_id]['cx'] = new_cx
            self.objects[obj_id]['cy'] = new_cy
            self.objects[obj_id]['missed'] = 0
            self.objects[obj_id]['rect'] = input_rects[inp_idx]

            trail = self.objects[obj_id]['trail']
            trail.append((new_cx, new_cy))
            if len(trail) > 15:
                trail.pop(0)

            used_objects.add(obj_idx)
            used_inputs.add(inp_idx)

        # Register unmatched inputs as new
        for j in range(len(input_centroids)):
            if j not in used_inputs:
                cx, cy = input_centroids[j]
                self._register(cx, cy, input_rects[j])

        # Increment missed for unmatched existing objects
        for i in range(len(obj_ids)):
            if i not in used_objects:
                obj_id = obj_ids[i]
                self.objects[obj_id]['missed'] += 1
                if self.objects[obj_id]['missed'] > max_missed:
                    del self.objects[obj_id]

        return fall_detected, self.objects

    def _register(self, cx, cy, rect):
        self.objects[self.next_id] = {
            'cx': cx, 'cy': cy,
            'fall_count': 0, 'missed': 0,
            'rect': rect,
            'trail': [(cx, cy)]
        }
        self.next_id += 1

    def get_tracked_objects(self):
        return self.objects

    def reset(self):
        self.objects.clear()
        self.next_id = 0
        self.prev_gray = None
        logger.info("Tracker reset")


def create_fall_tracker():
    return FallTracker()
