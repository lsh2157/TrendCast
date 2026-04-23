from pymongo import MongoClient
import re

client = MongoClient('mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0', tlsAllowInvalidCertificates=True)
db = client['trendcast']

PAIRS = [
    ('uncleaned_articles_nyt', 'cleaned_nyt'),
    ('uncleaned_articles_news', 'cleaned_newsapi'),
]

for src_name, dst_name in PAIRS:
    src = db[src_name]
    dst = db[dst_name]
    dst.drop()

    total = src.count_documents({})
    print(f"\nCleaning {src_name} ({total} docs) -> {dst_name}")

    inserted = skipped = 0
    for doc in src.find({}):
        doc.pop('_id', None)

        if not doc.get('title') or len(doc.get('title', '')) < 10:
            skipped += 1
            continue

        if not doc.get('description') and not doc.get('content'):
            skipped += 1
            continue

        if doc.get('content'):
            doc['content'] = re.sub(r'\[\+\d+ chars\]', '', doc['content']).strip()

        doc['cleaned'] = True
        dst.insert_one(doc)
        inserted += 1

    print(f"  Inserted: {inserted} | Skipped: {skipped}")

# Clean amazon
print(f"\nCleaning amazon_reviews -> cleaned_amazon")
src = db['amazon_reviews']
dst = db['cleaned_amazon']
dst.drop()

inserted = skipped = 0
for doc in src.find({}):
    doc.pop('_id', None)
    if not doc.get('reviewText') or not doc.get('overall'):
        skipped += 1
        continue
    if len(doc.get('reviewText', '')) < 10:
        skipped += 1
        continue
    doc['cleaned'] = True
    dst.insert_one(doc)
    inserted += 1
    if inserted % 50000 == 0:
        print(f"  {inserted:,} inserted...")

print(f"  Inserted: {inserted:,} | Skipped: {skipped:,}")

print("\nFinal collections:")
for col in db.list_collection_names():
    print(f"  {col}: {db[col].count_documents({}):,}")

client.close()
