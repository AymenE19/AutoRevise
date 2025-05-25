# --- Imports ---
import json
import logging
from os.path import join

from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from functionalities import process_scribd_api_response, download_file_from_scribd
from scraping.settings import (
    SCRIBD_MAX_PARSABLE_PAGES, SCRIBD_API_BASE_URL, SCRIBD_PREFERRED_FILE_LENGTH, SCRIBD_LANGS, SCRIBD_FILE_TYPES,
    SCRAPING_ROOT_DOWNLOAD_PATH, SCRIBD_MAX_FILE_LENGTH, SCRIBD_MIN_FILE_LENGTH, SCRIBD_MAX_SAVED_RESULTS
)
from utils.files import sanitize_filename, ensure_directory_exists
from utils.logger import setup_logger
from utils.urls import build_url

# Logging Configuration
logger = setup_logger()

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Load the targeted topics
with open("topics.json", "r") as topics_file:
    topics = json.load(topics_file)


def run_scraping():
    for topic in topics:
        for subtopic in topics[topic]:

            # Configure temporal variables
            current_page = 1
            parsable_pages_count = 1  # Initialized to 1 but will get updated with the first API request
            docs_data = []
            topic_download_path = join(SCRAPING_ROOT_DOWNLOAD_PATH, sanitize_filename(subtopic))
            ensure_directory_exists(topic_download_path)

            logger.info(f"Downloading {subtopic} from {topic} pages into {topic_download_path}")
            chrome_options.add_experimental_option(
                "prefs",
                {
                    "download.default_directory": topic_download_path,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
            )

            # Iterating through the pages of Scribd API
            while current_page <= parsable_pages_count and current_page <= SCRIBD_MAX_PARSABLE_PAGES:
                # Build Scribd API URL
                api_url = build_url(
                    SCRIBD_API_BASE_URL,
                    query=subtopic,
                    num_pages=SCRIBD_PREFERRED_FILE_LENGTH,
                    language=SCRIBD_LANGS,
                    filetype=SCRIBD_FILE_TYPES,
                    page=current_page
                )

                # Get and reformat the response of Scribd API
                logging.info(f"Fetching data from Scribd API: {api_url}")
                api_response = get(api_url)
                processed_data, pages_count, current_page = process_scribd_api_response(api_response, subtopic)

                # Keep only the files with the desired pages count
                processed_data = filter(
                    lambda doc_data: SCRIBD_MIN_FILE_LENGTH <= doc_data["pages"] <= SCRIBD_MAX_FILE_LENGTH,
                    processed_data
                )

                # Extend the docs_data list with the new data and increment the parsable pages counter
                docs_data.extend(processed_data)
                current_page += 1

            # Sort the locally stored docs data by the views count of each document
            docs_data = sorted(docs_data, key=lambda doc: doc["pages"], reverse=True)

            # Keep less than SCRIBD_MAX_SAVED_RESULTS results
            docs_data = docs_data[:SCRIBD_MAX_SAVED_RESULTS]

            # Initiate the Chrome driver (It will be automatically downloaded if necessary)
            chrome_service = Service(ChromeDriverManager().install())
            chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            for idx, doc in enumerate(docs_data):
                download_file_from_scribd(doc, chrome_driver, topic_download_path)
            chrome_driver.quit()


if __name__ == "__main__":
    run_scraping()
