from pymongo import MongoClient

ATLAS_URI = "YOUR_MONGODB_ATLAS_URI_HERE"

client = MongoClient(ATLAS_URI)
db = client["trendcast"]
