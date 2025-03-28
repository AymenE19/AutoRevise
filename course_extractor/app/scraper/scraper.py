# Importing dependencies ________________________________________________________________________________________________
import os
import re
import time
from datetime import datetime, UTC
from urllib.parse import unquote

import requests
from dotenv import load_dotenv
from requests import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from AutoRevise.course_extractor.app.storage.database import AtlasClient
from AutoRevise.course_extractor.app.utils.files import sanitize_filename, ensure_directory_exists, rename_file
from AutoRevise.course_extractor.app.utils.logging import log_message
from AutoRevise.course_extractor.app.utils.urls import parameterized_url_generator

from AutoRevise.course_extractor.app.storage.models import CourseDocument

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Scribd API
SCRIBD_SEARCH_TERM = input("Write the desired search term (i.e. Cours de python) : ")
SCRIBD_API_BASE_URL = "https://www.scribd.com/search/query"
SCRIBD_MAX_PARSABLE_PAGES = int(os.getenv("SCRIBD_MAX_PARSABLE_PAGES"))
SCRIBD_MAX_SAVED_RESULTS = int(os.getenv("SCRIBD_MAX_SAVED_RESULTS"))
SCRIBD_LANGS = os.getenv("SCRIBD_LANGS").split(",")
SCRIBD_FILE_CATEGORY = os.getenv("SCRIBD_FILE_CATEGORY").split(",")

SCRIBD_FILE_TYPES = os.getenv("SCRIBD_FILE_TYPES").split(",")

SCRIBD_PREFERRED_FILE_LENGTH = os.getenv("SCRIBD_PREFERRED_FILE_LENGTH")
SCRIBD_MIN_FILE_LENGTH = int(os.getenv("SCRIBD_MIN_FILE_LENGTH"))
SCRIBD_MAX_FILE_LENGTH = int(os.getenv("SCRIBD_MAX_FILE_LENGTH"))

# Mongodb SetUp
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)

# Check the download folder
DOWNLOAD_PATH = os.path.join(os.getenv("DOWNLOAD_PATH"), sanitize_filename(SCRIBD_SEARCH_TERM))
ensure_directory_exists(DOWNLOAD_PATH)

# Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


# Defining necessary functions _________________________________________________________________________________________
def search_url_generator(search_term: str, page: int = 1):
    """Takes a search term and returns a URL with parameters"""

    return parameterized_url_generator(
        SCRIBD_API_BASE_URL,
        query=search_term,
        num_pages=SCRIBD_PREFERRED_FILE_LENGTH,
        language=SCRIBD_LANGS,
        filetype=SCRIBD_FILE_TYPES,
        page=page
    )



def process_scribd_docs_response(response: Response):
    json_response = response.json()

    # Extract the list of documents data from the returned json response
    docs_data_list = json_response["results"]["documents"]["content"]["documents"]

    # Reconstruct a new list that contains CourseDocument objects
    processed_docs_data = [
        CourseDocument(
            doc_id=doc["id"],
            file_name=f"{doc['id']}.pdf",
            file_path=os.path.join(sanitize_filename(SCRIBD_SEARCH_TERM), f"{doc['id']}.pdf"),
            file_type="pdf",
            title=doc["title"],
            url=doc["reader_url"],
            pages=doc["pageCount"],
            views=doc["views"]
        ).to_dict() for doc in docs_data_list
    ]

    # Return the processed docs data list, the total number of parsable pages and the current API page
    return processed_docs_data, json_response["page_count"], json_response["current_page"]


def pdf_downloader(doc_data: dict, chrome_driver: webdriver.Chrome):
    _id = doc_data["_id"]
    title = doc_data["title"]
    file_name = doc_data["file_name"]

    # Get the pdf display page using https://ilide.info/
    try:
        # Construire l'URL correctement en utilisant urllib.parse.quote pour encoder les caractères spéciaux dans le titre
        from urllib.parse import quote
        encoded_title = quote(title)

        ilide_url = parameterized_url_generator(
            "https://ilide.info/docgeneratev2",
            fileurl=f"https://scribd.vdownloaders.com/pdownload/{_id}/{encoded_title}",
            title=encoded_title,
            utm_source="scrfree",
            utm_medium="queue",
            utm_campaign="dl"
        )

        log_message(f"PDFs Downloading | Accessing ilide.info with URL: {ilide_url}")
        chrome_driver.get(ilide_url)

        # Attendre que la page se charge complètement
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )

        # Extract the pdf viewer page URL from the current page
        pdf_viewer_page_url = None
        iframes = chrome_driver.find_elements(By.TAG_NAME, "iframe")

        log_message(f"PDFs Downloading | Found {len(iframes)} iframes on the page")

        for iframe in iframes:
            src = iframe.get_attribute("src")
            log_message(f"PDFs Downloading | Iframe source: {src}")
            if src and src.startswith("https://ilide.info/viewer/web/viewer.html?file="):
                pdf_viewer_page_url = src
                break

        if not pdf_viewer_page_url:
            log_message(f"PDFs Downloading | No PDF viewer URL found for document {_id}")
            return False

        # Redirect to the pdf viewer page
        log_message(f"PDFs Downloading | Redirecting to {pdf_viewer_page_url}")
        chrome_driver.get(pdf_viewer_page_url)

        # Wait for the page to load
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "download"))
        )

        # Click on the download button
        download_button = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.ID, "download"))
        )
        download_button.click()

        # Extract the original download filename from the pdf viewer page URL
        decoded_pdf_viewer_page_url = unquote(pdf_viewer_page_url)
        match = re.search(
            r"https://ilide\.info/docdownloadv2-([^?]+)",
            decoded_pdf_viewer_page_url
        )

        if not match:
            log_message(
                f"PDFs Downloading | Could not extract filename pattern from URL: {decoded_pdf_viewer_page_url}")
            return False

        download_filename = match.group(1)
        if download_filename:  # Only rename the downloaded file if the original filename was extracted successfully
            download_filename = f"ilide.info-{download_filename}.pdf"
            log_message(f"PDFs Downloading | Extracted download filename: {download_filename}")

            # Wait for file download to complete (max 60 seconds)
            download_path = os.path.join(DOWNLOAD_PATH, download_filename)
            wait_time = 0
            max_wait = 60  # seconds
            while not os.path.exists(download_path) and wait_time < max_wait:
                log_message(f"PDFs Downloading | File not found yet, waiting... ({wait_time}/{max_wait}s)")
                time.sleep(5)  # Check every 5 seconds
                wait_time += 5

            if not os.path.exists(download_path):
                log_message(f"PDFs Downloading | Download timed out for {download_filename}")
                return False

            # Rename the newly downloaded file
            new_path = os.path.join(DOWNLOAD_PATH, file_name)
            rename_file(download_path, new_path)
            log_message(f"PDFs Downloading | Renamed file '{download_filename}' to '{file_name}'")
            return True
        else:
            log_message(f"PDFs Downloading | Failed to extract download filename")
            return False

    except Exception as e:
        log_message(f"PDFs Downloading | Error during download: {str(e)}")
        return False

def scrap_data_and_download_pdfs():
    # Fetching the list of Scribd file URLs ____________________________________________________________________________
    current_page = 1
    pages_count = None
    docs_data = []

    # Iterate through every API page and save the results into the temporary docs_data variable
    while True:
        log_message(f"Start of scraping API page {current_page} / {pages_count}")
        start_time = time.time()

        page_response = requests.get(
            parameterized_url_generator(
                SCRIBD_API_BASE_URL,
                query=SCRIBD_SEARCH_TERM,
                num_pages=SCRIBD_PREFERRED_FILE_LENGTH,
                language=SCRIBD_LANGS,
                filetype=SCRIBD_FILE_TYPES,
                page=current_page
            )
        )
        processed_data, pages_count, current_page = process_scribd_docs_response(page_response)

        # Insert the processed data into the temporary docs_data variable
        docs_data.extend(processed_data)

        elapsed_time = time.time() - start_time
        log_message(f"End of scraping API page ({elapsed_time:.2f}s) {current_page} / {pages_count}\n")

        # Increment the page counter then check if all parsable pages are done
        current_page += 1
        if pages_count is not None and (current_page > pages_count or current_page > SCRIBD_MAX_PARSABLE_PAGES):
            break

    # Sort the locally stored docs data by the views count of each document
    docs_data = sorted(docs_data, key=lambda doc: doc["pages"], reverse=True)

    # Drop the documents with less than 100 pages or more than 400 pages
    docs_data = [doc for doc in docs_data if SCRIBD_MIN_FILE_LENGTH <= doc["pages"] <= SCRIBD_MAX_FILE_LENGTH]

    # Keep less than SCRIBD_MAX_SAVED_RESULTS results
    docs_data = docs_data[:SCRIBD_MAX_SAVED_RESULTS]

    # Install the chrome driver if necessary then initiate it __________________________________________________________
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for idx, doc in enumerate(docs_data):
        # Log the start of the document downloading process
        log_message(f"Start of PDF file downloading & doc data inserting {idx+1}/{len(docs_data)}: {doc['url']}")
        start_time = time.time()

        pdf_downloader(doc, driver)

        # Insert the new processed document's data into the database
        mongodb_client.insert_one(MONGODB_COLLECTION_NAME, doc, ignore_duplicates=True)

        elapsed_time = time.time() - start_time
        log_message(f"End of PDF file downloading & doc data inserting ({elapsed_time:.2f}s) {idx+1}/{len(docs_data)}: {doc['url']}\n")

    driver.quit()