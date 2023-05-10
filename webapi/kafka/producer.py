from confluent_kafka import Producer
from webapi.kafka.config import kafka_connection_producer

producer = Producer(kafka_connection_producer)

def produce_message(topic, message):
    producer.produce(topic, message)
    producer.flush()

def retry_message(topic, message):
    # Send message to retry topic
    producer.produce(f'retry_{topic}', message)
    producer.flush()
