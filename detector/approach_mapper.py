from detector.roi_config import ROIS

def get_bbox_center(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def assign_approach(detections):
    assigned = []

    for det in detections:
        cx, cy = get_bbox_center(det["bbox"])

        for approach, (x1, y1, x2, y2) in ROIS.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                assigned.append({
                    "label": det["label"],
                    "bbox": det["bbox"],
                    "approach": approach
                })
                break

    return assigned
