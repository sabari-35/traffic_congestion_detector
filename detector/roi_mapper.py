

ROIS = {
    "N": (0, 0, 720, 300),       
    "S": (0, 900, 720, 1280),    
    "E": (450, 300, 720, 900),    
    "W": (0, 600, 270, 900)       
}


def assign_approach(cx, cy):
    """
    Assign object to N/S/E/W based on center point
    """
    for approach, (x1, y1, x2, y2) in ROIS.items():
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return approach
    return None
