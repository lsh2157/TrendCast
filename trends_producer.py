from pytrends.request import TrendReq
import json
import time
from kafka import KafkaProducer

# I pick 10 representative keywords.
GOLDEN_KEYWORDS = [
    "Apple", "NVIDIA", "Samsung", "Logitech",   # Companies
    "smartphone", "laptop", "smartwatch",       # Categories
    "OLED monitor", "mechanical keyboard", "noise cancelling headphones" # Features
]

KAFKA_TOPIC = 'trends_topic'

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

pytrends = TrendReq(hl='en-US', tz=360)

def fetch_golden_trends():
    print(f"--- Starting Golden Trends Ingestion at {time.ctime()} ---")
    
    for word in GOLDEN_KEYWORDS:
        print(f"Fetching Google Search Index for: {word}...")
        try:
            pytrends.build_payload([word], timeframe='now 7-d')
            data = pytrends.interest_over_time()
            
            if not data.empty:
                latest_index = int(data[word].iloc[-1])
                payload = {
                    'keyword': word,
                    'search_index': latest_index,
                    'timestamp': time.ctime(),
                    'source': 'Google Trends'
                }
                producer.send(KAFKA_TOPIC, value=payload)
                print(f"  🔥 {word} Search Index: {latest_index}")
            

            time.sleep(15)
            
        except Exception as e:
            print(f"  ❌ Error for {word}: {e}")
            time.sleep(60)

    producer.flush()
    print("--- Member 1 Data Collection DONE---")

if __name__ == "__main__":
    fetch_golden_trends()