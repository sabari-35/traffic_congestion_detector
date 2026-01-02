"""
Post-processing for YOLO object detection for traffic monitoring
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

class YOLOTrafficProcessor:
    def __init__(self, class_names: List[str], roi_zones: List[Tuple]):
        self.class_names = class_names
        self.roi_zones = roi_zones  # Regions of interest for different approaches
        
    def count_vehicles_by_zone(self, detections: List, frame_shape: Tuple) -> Dict:
        """Count vehicles in each approach zone"""
        zone_counts = defaultdict(lambda: defaultdict(int))
        
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # Find which zone the vehicle is in
            for zone_id, zone_polygon in enumerate(self.roi_zones):
                if self._point_in_polygon(center_x, center_y, zone_polygon):
                    vehicle_type = self.class_names[int(cls)]
                    zone_counts[zone_id][vehicle_type] += 1
                    break
        
        return zone_counts
    
    def estimate_queue_length(self, detections: List, approach_direction: str) -> float:
        """Estimate queue length based on vehicle positions"""
        if not detections:
            return 0.0
        
        relevant_detections = []
        for det in detections:
            if self.class_names[int(det[5])] in ['car', 'bus', 'truck']:
                relevant_detections.append(det)
        
        if approach_direction == 'N':
            positions = [det[3] for det in relevant_detections]  # y2 positions
            return max(positions) - min(positions) if positions else 0
        
        # Similar logic for other directions
        return 0.0
    
    def _point_in_polygon(self, x: float, y: float, polygon: List[Tuple]) -> bool:
        """Check if point is inside polygon"""
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside