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
    # value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    api_version=(0, 10, 2), 
    request_timeout_ms=30000
)

try:

    url = "mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0"
    client = MongoClient(url)
    db = client['trendcast']
    mongo_col_nyt = db['uncleaned_articles_nyt']
    mongo_col_news = db['uncleaned_articles_news']
    # mongo_client = MongoClient("mongodb://localhost:27017/")
    # mongo_col = mongo_client['TrendCastDB']['articles']
    print("✅ MongoDB connection succeeded")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

sql_conn = None
sql_cur = None
try:
    CLOUD_POSTGRES_URI="postgresql://postgres:trendcast2026@db.ukpznrrkocrvoeozpzeu.supabase.co:5432/postgres"
    sql_conn = psycopg2.connect(CLOUD_POSTGRES_URI)
    sql_cur = sql_conn.cursor() 
    

    sql_cur.execute("""
        CREATE TABLE IF NOT EXISTS google_trends_04_20 (
            keyword TEXT,
            timestamp TEXT,
            search_index INT,
            CONSTRAINT unique_keyword_timestamp UNIQUE (keyword, timestamp)
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
        try:
            raw_data = message.value.decode('utf-8')
            data = json.loads(raw_data)
        except Exception as e:
            print(f"⚠️  Skipping invalid message: {e}")
            continue # Skip if not able to deserialize data

        topic = message.topic

        if topic == "news_topic":
            #continue
            mongo_col_news.insert_one(data)
            print(f"📥 [Mongo] news saved: {data.get('title', 'Untitled')[:30]}...")
        if topic == 'nyt_topic':
            #continue
            mongo_col_nyt.insert_one(data)
            print(f"📥 [Mongo] nyt saved: {data.get('title', 'Untitled')[:30]}...")
            
        elif topic == 'trends_topic':
            if sql_cur:
                try:
                    keyword = data.get('keyword', 'Unknown')
                    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    search_index = data.get('search_index', 0)
                    sql_cur.execute("""
                        INSERT INTO google_trends_04_20 (keyword, timestamp, search_index) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (keyword, timestamp) DO NOTHING;
                    """, (keyword, timestamp, search_index))
                    sql_conn.commit()
                    print(f"📊 [SQL] saved trends: {keyword}")
                    print("""keyword: %s, timestamp: %s, search_index: %s""" % (keyword, timestamp, search_index))
                except Exception as e:
                    if sql_conn: sql_conn.rollback()
                    print(f"❌ SQL write error: {e}")
            else:
                print(f"⏩ skip SQL write (not connected): {data.get('keyword', 'Unknown')}")
    print("Completed")

except KeyboardInterrupt:
    print("\n👋 Consumer stopped by user.")
finally:
    if sql_cur: sql_cur.close()
    if sql_conn: sql_conn.close()
    if 'mongo_client' in locals(): mongo_client.close()