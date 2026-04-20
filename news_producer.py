import requests
import json
import time
from kafka import KafkaProducer

API_KEY = '94b7e70bf5cf4815ad50b095d98f9924' 


KEYWORD_MAP = {
    "Category": [
        "smartphone", "laptop", "tablet", "smartwatch", 
        "earbuds", "monitor", "smart TV", "streaming stick"
    ],
    "Company": [
        "Apple", "NVIDIA", "Samsung", "Sony", 
        "Microsoft", "Intel", "AMD", "Logitech"
    ],
    "Feature": [
        "noise cancelling headphones", "OLED monitor", 
        "mechanical keyboard", "wireless charger", 
        "4K webcam", "bluetooth speaker"
    ]
}

KAFKA_TOPIC = 'news_topic'


producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_and_send_news():
    print(f"--- Starting Multi-Tier News Ingestion at {time.ctime()} ---")
    
    for c_type, words in KEYWORD_MAP.items():
        for word in words:
            print(f"[{c_type}] Fetching: {word}...")
            
            url = f'https://newsapi.org/v2/everything?q={word}&language=en&pageSize=5&apiKey={API_KEY}'
            
            try:
                response = requests.get(url)
                data = response.json()
                
                if data.get('status') == 'ok':
                    articles = data.get('articles', [])
                    for art in articles:
                        payload = {
                            'type': c_type,      
                            'keyword': word,
                            'title': art['title'],
                            'url': art['url'],
                            'source': art['source']['name'],
                            'publishedAt': art['publishedAt'],
                            'description': art['description']
                        }
                        producer.send(KAFKA_TOPIC, value=payload)
                    print(f"  ✅ Sent {len(articles)} articles")
                else:
                    print(f"  ❌ API Error for {word}: {data.get('message')}")
            except Exception as e:
                print(f"  ⚠️ Request failed for {word}: {e}")
            

            time.sleep(1.5)

    producer.flush()
    print(f"--- Finished All Groups at {time.ctime()} ---")

if __name__ == "__main__":
    fetch_and_send_news()