kafka_config = {
    "bootstrap.servers": "broker:29092",
    "group.id": "analytics_group",
    "auto.offset.reset": "earliest",
}


kafka_topics = ["analytics-updates"]
