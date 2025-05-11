import os
import requests
import pandas as pd
import logging
import time
import re

from Utils.utils import random_delay
from Utils.network_utils import get_random_headers, circuit_breaker

# Setup logging
log_directory = "Logs/"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, "image_scraper.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# Image output directory
image_directory = "Images/"
os.makedirs(image_directory, exist_ok=True)

def sanitize_filename(name):
    """Sanitize title to be a valid filename."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:100]  # Limit filename length too

def download_image(url, path):
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            logging.info(f"✅ Image saved: {path}")
        else:
            logging.warning(f"⚠️ Failed to fetch {url} (status code {response.status_code})")
    except requests.RequestException as e:
        logging.error(f"❌ Request error for {url}: {e}")

def scrape_images():
    logging.info("🚀 Starting image download...")

    # ⏳ Load CSV *after* spider runs
    csv_file = "Data/geo.csv"
    if not os.path.exists(csv_file):
        logging.error(f"❌ CSV file not found: {csv_file}")
        return

    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():
        circuit_breaker()
        random_delay()

        title = str(row.get('Title', '')).strip()
        img_url = str(row.get('Article Image URL', '')).strip()

        if not title or not img_url or pd.isna(img_url):
            continue

        filename = sanitize_filename(title) + ".jpg"
        filepath = os.path.join(image_directory, filename)

        if os.path.exists(filepath):
            logging.info(f"⏭️ Skipping existing image: {filename}")
            continue

        download_image(img_url, filepath)

    logging.info("🏁 Image download complete.")
