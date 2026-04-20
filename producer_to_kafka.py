import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def stream_data(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"starting to stream {len(data)} records...")
        
        for record in data:
            source = record.get('source', '')

            
            if source == "Google Trends":
                topic = 'trends_topic'
            
            elif source == "New York Times":
                topic = 'nyt_topic'
            
            else:
                topic = 'news_topic'
            
            producer.send(topic, value=record)
            
            identifier = record.get('title', record.get('keyword', 'Unknown'))
            print(f"[{topic}] 发送成功: {identifier[:50]}...")
            

            time.sleep(0.1)
            
        producer.flush()
        print("\n--- All data has been successfully streamed to Kafka ---")

    except Exception as e:
        print(f"Error during streaming: {e}")

if __name__ == "__main__":
    stream_data('final_cleaned_data.json')