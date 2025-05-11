import streamlit as st
import pandas as pd
import os
from PIL import Image
import subprocess
from Scraper.ImagesScraper.GeoImage import sanitize_filename

DATA_PATH = 'Data/geo.csv'
IMAGE_DIR = 'Images/'

@st.cache_data
def load_csv():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame()

def run_scraper():
    # Run the spider (GeoSpider must be invoked via CLI or subprocess)
    subprocess.run(["scrapy", "crawl", "geo"], cwd=os.getcwd())

    # Run the image downloader
    subprocess.run(["python", "GeoImage.py"], cwd=os.getcwd())

def find_article_by_link(df, link):
    return df[df['link'] == link].iloc[0] if link in df['link'].values else None

def display_article(article):
    title = article['Title']
    st.subheader(title)

    # Show Image
    filename = sanitize_filename(title) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(image_path):
        st.image(Image.open(image_path), use_column_width=True)
    else:
        st.warning("Image not found.")

    # Show Text
    st.write(f"**Date:** {article['Date']}")
    st.markdown(f"**Link:** [View Article]({article['Link']})")
    st.markdown("### Article Content")
    st.write(article['Article Text'])

def main():
    st.title("Geo TV Article Viewer")

    df = load_csv()

    st.subheader("Search Article by Link")
    input_link = st.text_input("Paste Geo TV article link")

    if input_link:
        article = find_article_by_link(df, input_link)

        if article is not None:
            st.success("✅ Article found in CSV")
            display_article(article)
        else:
            st.warning("🔄 Article not found. Trying to scrape now...")
            run_scraper()
            df = load_csv()  # Reload after scraping
            article = find_article_by_link(df, input_link)

            if article is not None:
                st.success("✅ Article scraped successfully!")
                display_article(article)
            else:
                st.error("❌ Article still not found. It might not be available or scraping failed.")

if __name__ == "__main__":
    main()
