from pymongo import MongoClient, ASCENDING, TEXT
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["trendcast"]

print("Creating collections and indexes...")

news = db["news_articles"]
news.create_index([("title", TEXT), ("content", TEXT)], name="text_search")
news.create_index([("publishedAt", ASCENDING)], name="date_index")
news.create_index([("url", ASCENDING)], unique=True, name="url_unique")
print("  news_articles done")

nyt = db["nytimes_articles"]
nyt.create_index([("headline", TEXT), ("abstract", TEXT)], name="text_search")
nyt.create_index([("pub_date", ASCENDING)], name="date_index")
nyt.create_index([("web_url", ASCENDING)], unique=True, name="url_unique")
print("  nytimes_articles done")

amazon = db["amazon_reviews"]
amazon.create_index([("asin", ASCENDING), ("reviewTime", ASCENDING)], name="asin_date")
amazon.create_index([("reviewText", TEXT)], name="text_search")
print("  amazon_reviews done")

print("\nAll collections ready:")
for name in db.list_collection_names():
    print(f"  - {name}")
client.close()
