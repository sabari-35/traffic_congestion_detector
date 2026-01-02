"""
Traffic Engineering Constants and Configuration
Based on Indian Roads Congress (IRC) standards and Highway Capacity Manual (HCM)
"""

class TrafficConstants:
    # Vehicle priority coefficients (Passenger Car Units)
    VEHICLE_PCU = {
        'car': 1.0,
        'motorcycle': 0.5,
        'auto': 0.8,
        'bus': 3.0,
        'truck': 3.5,
        'bicycle': 0.5,
        'pedestrian': 0.2
    }
    
    # Saturation flow rates (vehicles/hour/lane)
    SATURATION_FLOW = {
        'urban': 1800,    # Urban areas
        'suburban': 2000, # Suburban areas
        'rural': 1600     # Rural areas
    }
    
    # Safety constraints (seconds)
    MIN_GREEN_TIME = 15
    MAX_GREEN_TIME = 120
    MIN_PEDESTRIAN_TIME = 7
    YELLOW_TIME = 3
    ALL_RED_TIME = 2
    
    # Congestion levels and adjustments
    CONGESTION_LEVELS = {
        'free': 0.9,
        'stable': 1.0,
        'congested': 1.2,
        'severely_congested': 1.5
    }
    
    # Cycle time ranges (seconds)
    MIN_CYCLE_TIME = 60
    MAX_CYCLE_TIME = 180
    DEFAULT_CYCLE_TIME = 120
    
    # Spillback thresholds
    QUEUE_SPILLBACK_RATIO = 0.8  # 80% of link length
    CRITICAL_DENSITY = 150  # PCU/km/lane