kafka_config = {
    "bootstrap.servers": "broker:29092",
    "acks": "all",
    "retries": 3,
    "group.id": "analytics_group",
}

kafka_topics = ["analytics-updates"]
