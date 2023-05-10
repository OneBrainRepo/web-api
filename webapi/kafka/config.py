"""
Define Kafka connection configs here
"""
import os

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "localhost")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "group1")
MAX_RETRIES=os.getenv("MAX_RETRIES", 5)
RETRY_DELAY=os.getenv("RETRY_DELAY", 15)

# Configs
kafka_connection_client = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': KAFKA_GROUP_ID,
    'auto.offset.reset': 'earliest'
}
kafka_connection_producer = {
    'bootstrap.servers': BOOTSTRAP_SERVERS
}