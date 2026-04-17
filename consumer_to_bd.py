import json
from kafka import KafkaConsumer
from pymongo import MongoClient
import psycopg2
import sys
from datetime import datetime  

consumer = KafkaConsumer(
    'news_topic', 'nyt_topic', 'trends_topic',
    bootstrap_servers=['127.0.0.1:9092'], 
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    api_version=(0, 10, 2), 
    request_timeout_ms=30000
)

try:
    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_col = mongo_client['TrendCastDB']['articles']
    print("✅ MongoDB connection succeeded")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

sql_conn = None
sql_cur = None
try:
    sql_conn = psycopg2.connect(
        host="127.0.0.1", 
        database="trendcast", 
        user="postgres", 
        password=None,
        port="5432" 
    )
    sql_cur = sql_conn.cursor() 
    

    sql_cur.execute("""
        CREATE TABLE IF NOT EXISTS google_trends (
            keyword TEXT,
            timestamp TEXT,
            search_index INT
        );
    """)
    sql_conn.commit()

    
    print("✅ PostgreSQL connection succeeded")
except Exception as e:
    print(f"❌ SQL Connection Failed: {e}")
    print("⚠️  Consumer will continue, but Trends data will be skipped.")

print("🚀 Consumer starting! Waiting for Kafka messages...")

try:
    for message in consumer:
        data = message.value
        topic = message.topic
        
        if topic in ['news_topic', 'nyt_topic']:
            mongo_col.insert_one(data)
            print(f"📥 [Mongo] saved: {data.get('title', 'Untitled')[:30]}...")
            
        elif topic == 'trends_topic':
            if sql_cur:
                try:
                    keyword = data.get('keyword', 'Unknown')
                    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    search_index = data.get('search_index', 0)
                    
                    sql_cur.execute(
                        "INSERT INTO google_trends (keyword, timestamp, search_index) VALUES (%s, %s, %s)",
                        (keyword, timestamp, search_index)
                    )
                    sql_conn.commit()
                    print(f"📊 [SQL] saved trends: {keyword}")
                except Exception as e:
                    if sql_conn: sql_conn.rollback()
                    print(f"❌ SQL write error: {e}")
            else:
                print(f"⏩ skip SQL write (not connected): {data.get('keyword', 'Unknown')}")

except KeyboardInterrupt:
    print("\n👋 Consumer stopped by user.")
finally:
    if sql_cur: sql_cur.close()
    if sql_conn: sql_conn.close()
    if 'mongo_client' in locals(): mongo_client.close()