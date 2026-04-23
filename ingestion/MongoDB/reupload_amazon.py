from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
local = MongoClient(os.getenv("MONGO_URI"))["trendcast"]["amazon_reviews"]
atlas = MongoClient('mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0', tlsAllowInvalidCertificates=True)["trendcast"]

# Drop old cleaned_amazon
atlas["cleaned_amazon"].drop()
print("Dropped old cleaned_amazon")

# Upload in large batches - only records with product_title
batch = []
inserted = 0
BATCH_SIZE = 5000

for doc in local.find({"product_title": {"$exists": True}}):
    doc.pop("_id", None)
    batch.append(doc)
    if len(batch) >= BATCH_SIZE:
        atlas["cleaned_amazon"].insert_many(batch, ordered=False)
        inserted += len(batch)
        batch = []
        print(f"  Uploaded {inserted:,}...")

if batch:
    atlas["cleaned_amazon"].insert_many(batch, ordered=False)
    inserted += len(batch)

print(f"\nDone! Uploaded {inserted:,} enriched reviews to Atlas")
print(f"Atlas cleaned_amazon: {atlas['cleaned_amazon'].count_documents({}):,}")
