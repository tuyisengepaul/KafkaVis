from confluent_kafka import Producer
import json
import time
import random
 
# Kafka configuration
bootstrap_servers = 'localhost:9092'
topic = 'network-events'
 
# Create Kafka producer configuration
conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'network-events-producer'
        }
 
# Create Kafka producer instance
producer = Producer(conf)
 
def delivery_report(err, msg):
    """Delivery report callback called on producing completion."""
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
 
def generate_network_data():
    """Generate simulated network data."""
    data = {
        'timestamp': int(time.time()),
        'source_ip': '192.168.1.{}'.format(random.randint(1, 255)),
        'destination_ip': '10.0.0.{}'.format(random.randint(1, 255)),
        'data_size_kb': random.randint(1, 100),
        'protocol': 'TCP' if random.choice([True, False]) else 'UDP'
    }
    return json.dumps(data)
 
def produce_to_kafka(producer, topic, data):
    """Produce data to Kafka topic."""
    producer.produce(topic, value=data, callback=delivery_report)
    producer.poll(0)
 
def main():
    try:
        while True:
            network_data = generate_network_data()
            produce_to_kafka(producer, topic, network_data)
            time.sleep(2)  # Simulate data generation every second
 
    except KeyboardInterrupt:
        pass
    finally:
        print('Kafka producer flushed and closed.')
 
if __name__ == '__main__':
    main()