from detector.step6_signal_pipeline import run_signal_advisory

# Example output from STEP 5
queue_data = {
    "N": {"vehicles": {}, "queue_length": 0.0, "pedestrians": 0},
    "S": {
        "vehicles": {"car": 18, "bus": 4, "motorcycle": 6},
        "queue_length": 45.0,
        "pedestrians": 12
    },
    "E": {
        "vehicles": {"car": 8, "bus": 2},
        "queue_length": 20.0,
        "pedestrians": 5
    },
    "W": {
        "vehicles": {"car": 3},
        "queue_length": 8.0,
        "pedestrians": 2
    }
}

advice = run_signal_advisory(queue_data)
print(advice)
