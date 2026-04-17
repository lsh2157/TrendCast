from pymongo import MongoClient

ATLAS_URI = "mongodb+srv://ln2591_db_user:uXwCG4tq2dFsQwbW@cluster0.793zfrw.mongodb.net/trendcast?appName=Cluster0"

client = MongoClient(ATLAS_URI)
db = client["trendcast"]


def get_latest_news(limit=10):
    return list(
        db.news_articles.find(
            {},
            {
                "title": 1,
                "source": 1,
                "publishedAt": 1,
                "description": 1,
                "url": 1,
                "_id": 0,
            },
        ).sort("publishedAt", -1).limit(limit)
    )


def get_news_by_keyword(keyword, limit=10):
    return list(
        db.news_articles.find(
            {"keyword_matched": keyword},
            {
                "keyword_matched": 1,
                "source": 1,
                "publishedAt": 1,
                "description": 1,
                "url": 1,
                "_id": 0,
            },
        ).sort("publishedAt", -1).limit(limit)
    )


def search_news(query, limit=10):
    return list(
        db.news_articles.find(
            {"$text": {"$search": query}},
            {"title": 1, "source": 1, "publishedAt": 1, "url": 1, "_id": 0},
        ).limit(limit)
    )


def get_top_products(limit=10):
    pipeline = [
        {
            "$group": {
                "_id": "$asin",
                "avg_rating": {"$avg": "$overall"},
                "review_count": {"$sum": 1},
            }
        },
        {"$sort": {"review_count": -1}},
        {"$limit": limit},
    ]
    return list(db.amazon_reviews.aggregate(pipeline))


def get_rating_breakdown(limit=10):
    pipeline = [
        {"$group": {"_id": "$overall", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$limit": limit},
    ]
    return list(db.amazon_reviews.aggregate(pipeline))


def get_top_news_sources(limit=10):
    pipeline = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return list(db.news_articles.aggregate(pipeline))


def get_nyt_articles(from_date="2023-01-01", limit=10):
    return list(
        db.nytimes_articles.find(
            {"pub_date": {"$gte": from_date}},
            {"headline": 1, "pub_date": 1, "abstract": 1, "web_url": 1, "_id": 0},
        ).limit(limit)
    )


def get_keyword_trends():
    pipeline = [
        {"$group": {"_id": "$keyword_matched", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return list(db.news_articles.aggregate(pipeline))

if __name__ == "__main__":
    print(db.list_collection_names())