import requests
import json
import time
from kafka import KafkaProducer

NYT_KEY = 'Wg9bELNDAcYXYexFzHmOUVx2EZKJdvwHJbBd2hrsGJdhec2L' 
KAFKA_TOPIC = 'nyt_topic'

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

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_nyt_news():
    print(f"--- Starting NYT Article Ingestion at {time.ctime()} ---")
    
    for c_type, words in KEYWORD_MAP.items():
        for word in words:
            print(f"[{c_type}] Searching NYT for: {word}...")
            
            url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q={word}&api-key={NYT_KEY}"
            
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('response', {}).get('docs', [])
                    
                    count = 0
                    for art in articles[:3]:
                        payload = {
                            'type': c_type,
                            'keyword': word,
                            'title': art.get('headline', {}).get('main'),
                            'source': 'New York Times',
                            'publishedAt': art.get('pub_date'),
                            'description': art.get('abstract'),
                            'url': art.get('web_url')
                        }
                        producer.send(KAFKA_TOPIC, value=payload)
                        count += 1
                    print(f"  ✅ Sent {count} NYT articles for {word}")
                elif response.status_code == 429:
                    print("  ⚠️ Rate limit hit! Resting for 30 seconds...")
                    time.sleep(30)
                else:
                    print(f"  ❌ NYT Error: {response.status_code}")
                
            except Exception as e:
                print(f"  ⚠️ Request failed: {e}")
            

            time.sleep(6)

    producer.flush()
    print(f"--- Finished NYT Ingestion at {time.ctime()} ---")

if __name__ == "__main__":
    fetch_nyt_news()