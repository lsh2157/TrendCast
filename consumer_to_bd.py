import json
import sys
from datetime import datetime

from kafka import KafkaConsumer
from pymongo import MongoClient
import psycopg2

ATLAS_URI = "mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0"

def safe_json_deserializer(m):
    text = m.decode("utf-8").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(f"⚠️ Skipping invalid JSON message: {text[:80]}")
        return None


consumer = KafkaConsumer(
    "news_topic",
    "nyt_topic",
    "trends_topic",
    bootstrap_servers=["127.0.0.1:9092"],
    auto_offset_reset="earliest",
    value_deserializer=safe_json_deserializer,
    api_version=(0, 10, 2),
    request_timeout_ms=30000,
)

# MongoDB Atlas
try:
    mongo_client = MongoClient(ATLAS_URI)
    mongo_db = mongo_client["trendcast"]

    news_col = mongo_db["news_articles"]
    nyt_col = mongo_db["nytimes_articles"]

    # Match teammate's indexes
    news_col.create_index([("title", "text"), ("content", "text")])
    nyt_col.create_index([("headline", "text"), ("abstract", "text")])

    print("✅ MongoDB connection succeeded")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# Supabase PostgreSQL
sql_conn = None
sql_cur = None
try:
    sql_conn = psycopg2.connect(
        host="db.ukpznrrkocrvoeozpzeu.supabase.co",
        dbname="postgres",
        user="postgres",
        password="trendcast2026",
        port="5432",
        sslmode="require",
    )
    sql_cur = sql_conn.cursor()

    sql_cur.execute(
        """
        CREATE TABLE IF NOT EXISTS google_trends (
            keyword TEXT,
            timestamp TEXT,
            search_index INT
        );
        """
    )
    sql_conn.commit()

    print("✅ PostgreSQL connection succeeded")
except Exception as e:
    print(f"❌ SQL Connection Failed: {e}")
    print("⚠️ Consumer will continue, but Trends data will be skipped.")

print("🚀 Consumer starting! Waiting for Kafka messages...")

try:
    for message in consumer:
        data = message.value
        topic = message.topic

        if data is None:
            continue

        if topic == "news_topic":
            news_col.insert_one(data)
            print(f"📥 [Mongo news] saved: {data.get('title', 'Untitled')[:30]}...")

        elif topic == "nyt_topic":
            nyt_col.insert_one(data)
            headline = data.get("headline", "Untitled")
            print(f"📰 [Mongo NYT] saved: {headline[:30]}...")

        elif topic == "trends_topic":
            if sql_cur:
                try:
                    keyword = data.get("keyword", "Unknown")
                    timestamp = data.get(
                        "timestamp",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    search_index = data.get("search_index", 0)

                    sql_cur.execute(
                        """
                        INSERT INTO google_trends (keyword, timestamp, search_index)
                        VALUES (%s, %s, %s)
                        """,
                        (keyword, timestamp, search_index),
                    )
                    sql_conn.commit()
                    print(f"📊 [SQL] saved trends: {keyword}")
                except Exception as e:
                    if sql_conn:
                        sql_conn.rollback()
                    print(f"❌ SQL write error: {e}")
            else:
                print(f"⏩ skip SQL write (not connected): {data.get('keyword', 'Unknown')}")

except KeyboardInterrupt:
    print("\n👋 Consumer stopped by user.")
finally:
    if sql_cur:
        sql_cur.close()
    if sql_conn:
        sql_conn.close()
    if "mongo_client" in locals():
        mongo_client.close()