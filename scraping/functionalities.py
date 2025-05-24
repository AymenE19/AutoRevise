import os
import re
from datetime import datetime, UTC
from os.path import join
from time import sleep
from urllib.parse import unquote

from selenium.webdriver import Chrome

from requests import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.files import sanitize_filename, rename_file
from utils.logger import setup_logger
from utils.urls import build_url

# Logging Configuration
logger = setup_logger()


def process_scribd_api_response(response: Response, search_term: str) -> tuple[list, int, int]:
    """Process the Scribd API response and extract document data"""

    # Convert the raw json response into a Python dictionary
    json_response = response.json()

    # Extract the list of documents data from the returned json response
    docs_data_list = json_response["results"]["documents"]["content"]["documents"]

    # Reconstruct a new list that contains only the fields we want
    processed_docs_data = [
        {
            "_id": doc["id"],
            "file_name": f"{doc["id"]}.pdf",
            "file_path": join(sanitize_filename(search_term), f"{doc["id"]}.pdf"),
            "file_type": "pdf",
            "title": doc["title"],
            "url": doc["reader_url"],
            "pages": doc["pageCount"],
            "views": doc["views"],
            "creation_date": datetime.now(UTC)
        } for doc in docs_data_list
    ]

    # Return the processed docs data list, the total number of parsable pages and the current API page
    return (
        processed_docs_data,
        json_response["page_count"],
        json_response["current_page"]
    )


def download_file_from_scribd(doc_data: dict, chrome_driver: Chrome, download_dir: str):
    """Downloads the PDF document using the chrome driver"""
    _id = doc_data["_id"]
    title = doc_data["title"]
    file_name = doc_data["file_name"]

    # Build the pdf display page and download it using https://ilide.info/
    chrome_driver.get(
        build_url(
            "https://ilide.info/docgeneratev2",
            fileurl=f"https://scribd.vdownloaders.com/pdownload/{_id}/{title}",
            title=title,
            utm_source="scrfree",
            utm_medium="queue",
            utm_campaign="dl"
        )
    )

    # Extract the pdf viewer page URL from the current page
    pdf_viewer_page_url = ""
    for iframe_element in chrome_driver.find_elements(By.TAG_NAME, "iframe"):
        src = iframe_element.get_attribute("src")
        if src and src.startswith("https://ilide.info/viewer/web/viewer.html?file="):
            pdf_viewer_page_url = src
            break

    # Redirect to the pdf viewer page
    logger.info(f"Redirecting to {pdf_viewer_page_url}")
    chrome_driver.get(pdf_viewer_page_url)

    # Click on the download button
    download_button = WebDriverWait(chrome_driver, 5).until(EC.element_to_be_clickable((By.ID, "download")))
    download_button.click()

    # Extract the original download filename from the pdf viewer page URL
    decoded_pdf_viewer_page_url = unquote(pdf_viewer_page_url)
    download_filename = re.search(r"https://ilide\.info/docdownloadv2-([^?]+)", decoded_pdf_viewer_page_url).group(1)

    if download_filename:  # Only rename the downloaded file if the original filename was extracted successfully
        download_filename = f"ilide.info-{download_filename}.pdf"
        logger.info(f"Extracted download filename : {download_filename}")

        # Wait for file download to complete
        while download_filename not in os.listdir(download_dir):
            logger.warning("File not downloaded yet, waiting...")
            sleep(5)  # Check every 5 seconds

        # Rename the newly downloaded file
        rename_file(os.path.join(download_dir, download_filename), os.path.join(download_dir, file_name))
        logger.info(f"Renamed file '{download_filename}' to '{file_name}'")
