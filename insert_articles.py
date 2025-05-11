# databases/insert_articles.py

import pandas as pd
import logging
import os
from Utils.db_utils import get_article_collection

def insert_articles_from_csv(csv_path="Data/geo.csv"):
    if not os.path.exists(csv_path):
        logging.error(f"CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    collection = get_article_collection()

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        document = {
            "title": row.get("Title", "").strip(),
            "date": row.get("Date", "").strip(),
            "link": row.get("Link", "").strip(),
            "listing_image_url": row.get("Listing Image URL", "").strip(),
            "article_image_url": row.get("Article Image URL", "").strip(),
            "article_text": row.get("Article Text", "").strip()
        }

        # Skip if link is missing
        if not document["link"]:
            continue

        # Use link as unique identifier
        if collection.find_one({"link": document["link"]}):
            skipped += 1
            continue

        try:
            collection.insert_one(document)
            inserted += 1
        except Exception as e:
            logging.error(f"Error inserting document: {e}")

    logging.info(f"✅ DB insert complete: Inserted={inserted}, Skipped={skipped}")
