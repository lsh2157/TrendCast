from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import os

load_dotenv()
local = MongoClient(os.getenv("MONGO_URI"))["trendcast"]
atlas = MongoClient(os.getenv("ATLAS_URI"))["trendcast"]

# Only sync these small collections - skip amazon_reviews (too big)
COLLECTIONS = ["news_articles", "nytimes_articles", "google_trends"]

for col_name in COLLECTIONS:
    src = local[col_name]
    dst = atlas[col_name]
    total = src.count_documents({})
    print(f"\nSyncing {col_name} ({total:,} docs)...")
    inserted = skipped = 0
    for doc in src.find({}):
        doc.pop("_id", None)
        try:
            dst.insert_one(doc)
            inserted += 1
        except DuplicateKeyError:
            skipped += 1
    print(f"  Inserted: {inserted} | Skipped: {skipped}")

print("\nAtlas totals:")
for col in COLLECTIONS:
    print(f"  {col}: {atlas[col].count_documents({})}")

local.close()
atlas.close()
