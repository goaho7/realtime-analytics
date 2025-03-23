from random import randint, uniform
from datetime import datetime, timezone, timedelta


class EventGenerator:
    @staticmethod
    def generate_random_event():
        now = datetime.now(timezone.utc)
        cutoff_timestamp = int((now - timedelta(days=8)).timestamp())
        # cur_timestamp = int(datetime.now(timezone.utc).timestamp())

        return {
            "sensor_id": f"sensor_{randint(1, 10)}",
            "temperature": uniform(-20.0, 50.0),
            "humidity": uniform(0.0, 100.0),
            "noise_level": uniform(30.0, 120.0),
            "air_quality_index": randint(0, 500),
            "timestamp": cutoff_timestamp,
        }
