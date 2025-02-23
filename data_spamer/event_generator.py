from random import randint, uniform
from datetime import datetime, timezone


class EventGenerator:
    @staticmethod
    def generate_random_event():

        return {
            "sensor_id": f"sensor_{randint(1, 10)}",
            "temperature": uniform(-20.0, 50.0),
            "humidity": uniform(0.0, 100.0),
            "noise_level": uniform(30.0, 120.0),
            "air_quality_index": randint(0, 500),
            "timestamp": int(datetime.now(timezone.utc).timestamp())
        }
