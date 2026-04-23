import json, os, sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
collection = client["trendcast"]["amazon_reviews"]

JSONL_FILE = sys.argv[1] if len(sys.argv) > 1 else "Electronics.jsonl"
BATCH_SIZE = 1000
MAX_RECORDS = 500000

if not os.path.exists(JSONL_FILE):
    print(f"File not found: {JSONL_FILE}")
    sys.exit(1)

batch = []
total = 0
skipped = 0

print(f"Loading: {JSONL_FILE}")
print(f"Capped at {MAX_RECORDS:,} records\n")

with open(JSONL_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if total + len(batch) >= MAX_RECORDS:
            break
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not (r.get("text") or r.get("reviewText")):
            skipped += 1
            continue
        batch.append({
            "asin":       r.get("asin"),
            "reviewText": r.get("text") or r.get("reviewText"),
            "overall":    r.get("rating") or r.get("overall"),
            "reviewTime": r.get("timestamp") or r.get("reviewTime"),
            "verified":   r.get("verified_purchase") or r.get("verified", False),
            "summary":    r.get("title") or r.get("summary")
        })
        if len(batch) >= BATCH_SIZE:
            collection.insert_many(batch, ordered=False)
            total += len(batch)
            batch = []
            print(f"  Inserted {total:,} reviews...")

if batch:
    collection.insert_many(batch, ordered=False)
    total += len(batch)

print(f"\nDone! Inserted: {total:,} | Skipped: {skipped:,}")
print(f"Collection total: {collection.count_documents({})}")
client.close()
