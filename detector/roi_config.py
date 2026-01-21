import numpy as np

# ==============================
# Container size
# ==============================
CONTAINER_W = 960
CONTAINER_H = 540

# ==============================
# Container origins
# ==============================
CONTAINERS = {
    "E": (0, 0),                      # top-left
    "N": (CONTAINER_W, 0),            # top-right
    "S": (0, CONTAINER_H),            # bottom-left
    "W": (CONTAINER_W, CONTAINER_H),  # bottom-right
}

# ==============================
# Canonical ROI (same for all)
# ==============================
BASE_ROI = np.array([
    (80, 200),   # ⬅ move right
    (940, 200),
    (940, 630),
    (80, 630)
], dtype=np.int32)



# ==============================
# Build ROIs (global)
# ==============================
ROIS = {
    d: BASE_ROI + np.array(CONTAINERS[d])
    for d in CONTAINERS
}
