# import scrapy
# import logging
# import os
# import pandas as pd
# from datetime import datetime
# import time
# from scrapy.crawler import CrawlerProcess


# # Set up logging
# log_directory = "Logs/"
# os.makedirs(log_directory, exist_ok=True)
# log_file = os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}.log")
# logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# # Output directory
# csv_directory = "Data/"
# os.makedirs(csv_directory, exist_ok=True)
# csv_file = os.path.join(csv_directory, "geo.csv")


# class GeoSpider(scrapy.Spider):
#     name = 'geo'
#     start_urls = [
#         'https://www.geo.tv/category/pakistan',
#         'https://www.geo.tv/category/world',
#         'https://www.geo.tv/category/sports',
#         'https://www.geo.tv/category/showbiz'
#     ]

#     custom_settings = {
#         'ROBOTSTXT_OBEY': True,
#         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'LOG_ENABLED': False,
#     }

#     def __init__(self):
#         self.scraped_data = []
#         self.scraped_count = 0
#         self.missed_count = 0
#         self.start_time = time.time()

#     def parse(self, response):
#         articles = response.css('div.col-xs-6.col-sm-6.col-lg-6.col-md-6.singleBlock')

#         for article in articles:
#             title = article.css('div.entry-title h2::text').get()
#             date = article.css('span.date::text').get()
#             link = article.css('a::attr(href)').get()
#             image_url = article.css('img::attr(src)').get()

#             if title and date and link:
#                 yield response.follow(link, callback=self.parse_article_detail, meta={
#                     'title': title.strip(),
#                     'date': date.strip(),
#                     'link': link,
#                     'listing_image_url': image_url
#                 })
#             else:
#                 self.missed_count += 1

#         next_page = response.css('a.next::attr(href)').get()
#         if next_page:
#             yield response.follow(next_page, self.parse)

#     # def parse_article_detail(self, response):
#     #     content_area = response.css('div.content-area')
#     #     paragraphs = content_area.css('p::text').getall()
#     #     article_text = ' '.join([p.strip() for p in paragraphs if p.strip()])
#     #     article_image_url = content_area.css('img::attr(src)').get()

#     #     item = {
#     #         'Title': response.meta['title'],
#     #         'Date': response.meta['date'],
#     #         'Link': response.meta['link'],
#     #         'Listing Image URL': response.meta['listing_image_url'],
#     #         'Article Image URL': article_image_url,
#     #         'Article Text': article_text
#     #     }

#     #     self.scraped_data.append(item)
#     #     self.scraped_count += 1


#     def parse_article_detail(self, response):
#         content_area = response.css('div.content-area')

#         # Extract all text within <p> tags inside content-area
#         paragraphs = content_area.css('p::text').getall()
#         article_text = ' '.join([p.strip() for p in paragraphs if p.strip()])

#         # Extract the first image URL within content-area
#         article_image_url = content_area.css('img::attr(src)').get()

#         item = {
#             'Title': response.meta['title'],
#             'Date': response.meta['date'],
#             'Link': response.meta['link'],
#             'Listing Image URL': response.meta['listing_image_url'],
#             'Article Image URL': article_image_url,
#             'Article Text': article_text
#         }

#         self.scraped_data.append(item)
#         self.scraped_count += 1

#     def closed(self, reason):
#         if self.scraped_data:
#             df = pd.DataFrame(self.scraped_data)
#             df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)

#         total_time = time.time() - self.start_time
#         logging.info(f"Spider closed: {reason}")
#         logging.info(f"Total Articles Scraped: {self.scraped_count}")
#         logging.info(f"Total Articles Missed: {self.missed_count}")
#         logging.info(f"Total Time Taken: {total_time:.2f} seconds")

import scrapy
import logging
import os
import pandas as pd
from datetime import datetime
import time
from scrapy.crawler import CrawlerProcess

from Utils.utils import random_delay
from Utils.network_utils import get_random_headers, circuit_breaker

# Logging setup
log_directory = "Logs/"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

# Output directory
csv_directory = "Data/"
os.makedirs(csv_directory, exist_ok=True)
csv_file = os.path.join(csv_directory, "geo.csv")


class GeoSpider(scrapy.Spider):
    name = 'geo'
    start_urls = [
        'https://www.geo.tv/category/pakistan',
        'https://www.geo.tv/category/world',
        'https://www.geo.tv/category/sports',
        'https://www.geo.tv/category/showbiz'
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'Mozilla/5.0',
        'LOG_ENABLED': False,
        'DOWNLOAD_DELAY': 0.25,  # Just in case, Scrapy setting
    }

    def __init__(self):
        self.scraped_data = []
        self.scraped_count = 0
        self.missed_count = 0
        self.start_time = time.time()

    def parse(self, response):
        circuit_breaker()
        random_delay()

        articles = response.css('div.col-xs-6.col-sm-6.col-lg-6.col-md-6.singleBlock')

        for article in articles:
            title = article.css('div.entry-title h2::text').get()
            date = article.css('span.date::text').get()
            link = article.css('a::attr(href)').get()
            image_url = article.css('img::attr(src)').get()

            if title and date and link:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_article_detail,
                    headers=get_random_headers(),
                    meta={
                        'title': title.strip(),
                        'date': date.strip(),
                        'link': link,
                        'listing_image_url': image_url
                    }
                )
            else:
                self.missed_count += 1

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse, headers=get_random_headers())

    def parse_article_detail(self, response):
        circuit_breaker()
        random_delay()

        content_area = response.css('div.content-area')
        paragraphs = content_area.css('p::text, p *::text').getall()
        article_text = ' '.join([p.strip() for p in paragraphs if p.strip()])
        article_image_url = content_area.css('img::attr(src)').get()

        item = {
            'Title': response.meta['title'],
            'Date': response.meta['date'],
            'Link': response.meta['link'],
            'Listing Image URL': response.meta['listing_image_url'],
            'Article Image URL': article_image_url,
            'Article Text': article_text
        }

        self.scraped_data.append(item)
        self.scraped_count += 1

    def closed(self, reason):
        if self.scraped_data:
            df = pd.DataFrame(self.scraped_data)
            df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)

        total_time = time.time() - self.start_time
        logging.info(f"Spider closed: {reason}")
        logging.info(f"✅ Scraped: {self.scraped_count}, ❌ Missed: {self.missed_count}, ⏱️ Time: {total_time:.2f}s")

