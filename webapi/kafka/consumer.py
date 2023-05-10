from confluent_kafka import Consumer, KafkaException
from webapi.kafka.producer import retry_message
from webapi.kafka.config import kafka_connection_client, MAX_RETRIES, RETRY_DELAY
import time
consumer = Consumer(kafka_connection_client)

def consume_messages(topics, callbacks):
    consumer.subscribe(topics)

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                topic = msg.topic()
                if topic in callbacks:
                    success = False
                    for _ in range(MAX_RETRIES):
                        try:
                            callbacks[topic](msg.value())
                            success = True
                            break
                        except Exception as e:
                            print(f"Error processing message: {e}, retrying...")
                            time.sleep(RETRY_DELAY)
                    
                    if not success:
                        # If message still fails after retries, send it to retry topic
                        retry_message(topic, msg.value())
        except KeyboardInterrupt:
            break

    # Close down consumer to commit final offsets.
    consumer.close()
