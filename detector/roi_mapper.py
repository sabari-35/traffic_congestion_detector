# def assign_approach(x, y):
#     for approach, (x1,y1,x2,y2) in ROIS.items():
#         if x1 <= x <= x2 and y1 <= y <= y2:
#             return approach
#     return None
# Adjust these based on your camera view
# detector/roi_config.py

ROIS = {
    "N": (0, 0, 720, 300),        # top area
    "S": (0, 900, 720, 1280),     # bottom area
    "E": (450, 300, 720, 900),    # right area
    "W": (0, 300, 270, 900)       # left area
}


def assign_approach(cx, cy):
    """
    Assign object to N/S/E/W based on center point
    """
    for approach, (x1, y1, x2, y2) in ROIS.items():
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return approach
    return None
