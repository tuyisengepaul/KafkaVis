from confluent_kafka import Consumer, KafkaError
import json


bootstrap_servers = 'localhost:9092'
topic = 'network-events'

# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'network-events-id',  # Consumer group ID
    'auto.offset.reset': 'earliest'  # Start reading from the beginning of the topic
}

# Create Kafka consumer instance
consumer = Consumer(consumer_config)
consumer.subscribe([topic])

EVENTS = []

try:
    while True:
        msg = consumer.poll(2)  # Adjust the timeout as needed
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event, not an error
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        data = json.loads(msg.value())
        EVENTS.append(data)
        print(EVENTS)
        print("........................................")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
