from confluent_kafka import Consumer

def init_consumer(topic):
    # Set the Kafka broker address
    bootstrap_servers = 'localhost:9092'
    consumer_config = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': 'network-events-id',  # Consumer group ID
    }

    # Create Kafka consumer instance
    consumer = Consumer(consumer_config)
    consumer.subscribe([topic])
    print("Consumer initialized....")
    return consumer
    