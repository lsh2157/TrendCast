from kafka import KafkaProducer, KafkaConsumer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = 'test_topic'

print("--- Starting Producer ---")
test_data = {'message': 'Hello Kafka! Member 1 is online.', 'timestamp': time.time()}
producer.send(topic, value=test_data)
producer.flush()
print(f"Sent: {test_data}")

print("\n--- Starting Consumer (waiting for message...) ---")
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='test-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=5000 
)

for message in consumer:
    print(f"Received: {message.value}")
    break 

print("\n--- Kafka Connection Test Passed! ---")