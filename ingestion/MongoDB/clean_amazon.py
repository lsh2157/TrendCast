from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
collection = client["trendcast"]["amazon_reviews"]

print("=== Cleaning amazon_reviews ===\n")

# Step 1: Remove records missing reviewText or rating
result = collection.delete_many({
    "$or": [
        {"reviewText": None},
        {"reviewText": ""},
        {"overall": None}
    ]
})
print(f"Removed {result.deleted_count:,} records missing text or rating")

# Step 2: Remove records with very short reviews (less than 10 chars)
result = collection.delete_many({
    "$expr": {"$lt": [{"$strLenCP": {"$ifNull": ["$reviewText", ""]}}, 10]}
})
print(f"Removed {result.deleted_count:,} records with very short reviews")

# Step 3: Report final count
total = collection.count_documents({})
print(f"\nClean collection total: {total:,}")

# Step 4: Sample check
print("\nSample record after cleaning:")
sample = collection.find_one({"reviewText": {"$exists": True}})
if sample:
    print(f"  asin:       {sample.get('asin')}")
    print(f"  overall:    {sample.get('overall')}")
    print(f"  reviewTime: {sample.get('reviewTime')}")
    print(f"  reviewText: {str(sample.get('reviewText'))[:80]}...")

client.close()
print("\nCleaning done!")
