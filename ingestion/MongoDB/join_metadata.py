import json, gzip
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
col = client["trendcast"]["amazon_reviews"]

META_FILES = [
    "meta_Cell_Phones_and_Accessories.jsonl.gz",
    "meta_Electronics.jsonl.gz"
]

# Step 1: Build lookup dict asin -> metadata
print("Loading metadata files...")
meta_lookup = {}

for filepath in META_FILES:
    print(f"  Reading {filepath}...")
    with gzip.open(filepath, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                asin = item.get("parent_asin") or item.get("asin")
                if asin:
                    meta_lookup[asin] = {
                        "product_title": item.get("title"),
                        "main_category": item.get("main_category"),
                        "categories": item.get("categories"),
                        "price": item.get("price"),
                        "store": item.get("store"),
                        "features": item.get("features")
                    }
            except json.JSONDecodeError:
                continue

print(f"  Loaded {len(meta_lookup):,} products\n")

# Step 2: Update reviews with metadata
print("Updating reviews with product info...")
updated = not_found = 0

for doc in col.find({}, {"_id": 1, "asin": 1}):
    asin = doc.get("asin")
    meta = meta_lookup.get(asin)
    if meta:
        col.update_one({"_id": doc["_id"]}, {"$set": meta})
        updated += 1
    else:
        not_found += 1

    if (updated + not_found) % 50000 == 0:
        print(f"  Processed {updated+not_found:,}...")

print(f"\nDone!")
print(f"  Updated: {updated:,}")
print(f"  Not found in metadata: {not_found:,}")

# Show sample
sample = col.find_one({"product_title": {"$exists": True}})
if sample:
    print(f"\nSample updated record:")
    print(f"  asin: {sample.get('asin')}")
    print(f"  product_title: {sample.get('product_title')}")
    print(f"  main_category: {sample.get('main_category')}")
    print(f"  categories: {sample.get('categories')}")
    print(f"  price: {sample.get('price')}")

client.close()
