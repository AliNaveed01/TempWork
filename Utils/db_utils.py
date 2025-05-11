from pymongo import MongoClient, errors
import logging

def get_mongo_client(uri="mongodb://localhost:27017", timeout=5000):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout)
        client.server_info()  # Trigger exception if connection fails
        return client
    except errors.ServerSelectionTimeoutError as err:
        logging.error(f"❌ Could not connect to MongoDB: {err}")
        raise

def get_article_collection(db_name="geo_scraper", collection_name="articles"):
    client = get_mongo_client()
    db = client[db_name]
    return db[collection_name]
