import requests
import time

from event_generator import EventGenerator


event_enerator = EventGenerator()


while True:
    url = 'http://user-api:8000/api/event'
    message = event_enerator.generate_random_event()
    try:
        requests.post(url=url, json=message)
        pass
    except Exception as e:
        print(f'ERROR: {e}')
    time.sleep(1)
