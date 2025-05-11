import sys
import os
from scrapy.crawler import CrawlerProcess
from Scraper.GeoSpider import GeoSpider
from Scraper.ImagesScraper.GeoImage import scrape_images
import logging
import time
from Databases.insert_articles import insert_articles_from_csv


# Setup logging (shared across both)
log_directory = "Logs/"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, "main.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

def run_scrapy_spider():
    """Runs the Geo article spider"""
    logging.info("🚀 Step 1: Running Scrapy spider...")
    process = CrawlerProcess()
    process.crawl(GeoSpider)
    process.start()
    logging.info("✅ Step 1 complete.")


def run_image_scraper():
    logging.info("🕐 Waiting for data to be ready...")
    time.sleep(2)  # Optional delay
    logging.info("🚀 Step 2: Running image scraper...")
    scrape_images()



def run_db_insert():
    logging.info("🚀 Step 3: Inserting articles into MongoDB...")
    insert_articles_from_csv()
    logging.info("✅ Step 3 complete.")



if __name__ == '__main__':
    try:
        run_scrapy_spider()
        run_image_scraper()
        run_db_insert()
        logging.info("🎉 Full pipeline complete.")
    except Exception as e:
        logging.error(f"❌ Error in main pipeline: {e}")
        sys.exit(1)
