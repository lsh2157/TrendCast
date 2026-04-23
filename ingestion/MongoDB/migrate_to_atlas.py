from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

print("Connecting to local and Atlas...")
local = MongoClient(os.getenv("MONGO_URI"))["trendcast"]
atlas = MongoClient(os.getenv("ATLAS_URI"))["trendcast"]

COLLECTIONS = ["news_articles", "nytimes_articles", "amazon_reviews"]
BATCH_SIZE = 1000

for col_name in COLLECTIONS:
    src = local[col_name]
    dst = atlas[col_name]
    total = src.count_documents({})
    print(f"\nMigrating {col_name} ({total:,} docs)...")
    
    batch = []
    migrated = 0
    for doc in src.find({}):
        doc.pop("_id", None)
        batch.append(doc)
        if len(batch) >= BATCH_SIZE:
            dst.insert_many(batch, ordered=False)
            migrated += len(batch)
            batch = []
            print(f"  {migrated:,} / {total:,}")
    if batch:
        dst.insert_many(batch, ordered=False)
        migrated += len(batch)
    print(f"  Done! {migrated:,} docs migrated")

print("\nAll done! Atlas collections:")
for col_name in COLLECTIONS:
    count = atlas[col_name].count_documents({})
    print(f"  {col_name}: {count:,}")

local.close()
atlas.close()
