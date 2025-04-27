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

from course_extractor.app.storage.database import AtlasClient
from course_extractor.app.utils.files import sanitize_filename, ensure_directory_exists, rename_file
from course_extractor.app.utils.logging import log_message
from course_extractor.app.utils.urls import parameterized_url_generator

# Defining global variables and constants ______________________________________________________________________________
load_dotenv()  # take environment variables from .env

# Scribd API
# categories =  {
#     # "Python": [
#     #     "Introduction à Python",
#     #     "Installation de Python Anaconda VS Code Jupyter Notebook",
#     #     "Variables types de données Python",
#     #     "Opérateurs arithmétiques logiques comparaison Python",
#     #     "Conditions boucles Python",
#     #     "Fonctions manipulation données Python",
#     #     "Structures de données algorithmes Python",
#     #     "Programmation orientée objet Python",
#     #     "Bases de données SQLite Python"
#     # ],
#     "Java": [
#         "Introduction au langage Java",
#         "Programmation orientée objet Java",
#         "Collections exceptions Java",
#         "Bases de données JDBC Java"
#     ],
#     "Bases de données": [
#         "Modèle relationnel SQL",
#         "Modélisation diagrammes E/A normalisation",
#         "Requêtes SQL avancées JOIN GROUP BY sous-requêtes",
#         "Transactions sécurité bases de données",
#         "Connexion base de données JDBC PHP PDO"
#     ],
#     "Programmation Web": [
#         "Bases HTML CSS",
#         "Introduction PHP",
#         "Interaction bases de données PHP",
#         "Sessions cookies PHP",
#         "AJAX interactivité web"
#     ]
# }
categories = {
    "Python": [
        "Introduction à Python",
        "Installation de Python Anaconda VS Code Jupyter Notebook",
        "Variables et types de données en Python",
        "Opérateurs arithmétiques, logiques et de comparaison en Python",
        "Conditions et boucles en Python",
        "Fonctions et manipulation des données en Python",
        "Structures de données et algorithmes en Python",
        "Programmation orientée objet (POO) en Python",
        "Bases de données SQLite avec Python"
    ],
    "Java": [
        "Introduction au langage Java",
        "Programmation orientée objet (POO) en Java",
        "Héritage, encapsulation et interfaces en Java",
        "Collections et gestion des exceptions en Java",
        "Bases de données avec JDBC en Java"
    ],
    "Bases de données": [
        "Concepts fondamentaux et SQL",
        "Modèle relationnel et normalisation",
        "Requêtes SQL avancées : JOIN, GROUP BY, sous-requêtes",
        "Transactions et sécurité des bases de données",
        "Connexion aux bases de données via JDBC et PHP PDO"
    ],
    "Programmation Web": [
        "Bases de HTML et CSS",
        "Introduction à PHP : Syntaxe, variables, boucles, fonctions",
        "Interaction avec les bases de données en PHP",
        "Gestion des sessions et cookies en PHP",
        "AJAX et interactivité web"
    ],
    "Programmation Mobile Android": [
        "Introduction à Android Studio et architecture des applications",
        "Interfaces utilisateur : XML, vues, boutons, champs de texte",
        "Navigation et fragments en Android",
        "Bases de données locales : SQLite et SharedPreferences",
        "Fonctionnalités natives et déploiement : Localisation, caméra, APK"
    ],
    "Framework PHP Laravel": [
        "Introduction à Laravel et structure du projet",
        "Routage et gestion des contrôleurs en Laravel",
        "Modèles et bases de données : Migrations et ORM Eloquent",
        "Gestion des formulaires et validation en Laravel",
        "Création d’une API RESTful avec Laravel"
    ],
    "Programmation JavaScript": [
        "Bases de JavaScript moderne : Syntaxe ES6, manipulation du DOM",
        "Framework front-end : React.js ou Vue.js",
        "Développement backend avec Node.js et Express.js",
        "Connexion à une base de données avec Mongoose",
        "Développement d’une application complète en JavaScript"
    ],
    "Programmation Mobile avec JavaScript": [
        "Introduction à React Native et Ionic",
        "Interfaces utilisateur : Composants de base et navigation",
        "Gestion des données et APIs avec Axios",
        "Fonctionnalités natives : GPS, caméra, stockage",
        "Déploiement d’applications mobiles : APK et IPA"
    ]
}

# categories = {
#    "Framework PHP Laravel": [
#         "php laravel",
#         "cours php Laravel"
#     ],
#   "Programmation Mobile avec JavaScript": [
#       "cours React Native ",
#       "Ionic",
#       "API Axios"
#
#     ]
# }

# Loop through categories and download PDFs
for category, subcategories in categories.items():
    for subcategory in subcategories:
        SCRIBD_SEARCH_TERM = subcategory

        SCRIBD_API_BASE_URL = "https://www.scribd.com/search/query"
        SCRIBD_MAX_PARSABLE_PAGES = int(os.getenv("SCRIBD_MAX_PARSABLE_PAGES"))
        SCRIBD_MAX_SAVED_RESULTS = int(os.getenv("SCRIBD_MAX_SAVED_RESULTS"))
        SCRIBD_LANGS = os.getenv("SCRIBD_LANGS").split(",")
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
        DOWNLOAD_PATH = os.path.join(os.getenv("DOWNLOAD_PATH"), sanitize_filename(category))
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
            """Process the Scribd API response and extract document data"""
            json_response = response.json()

            # Extract the list of documents data from the returned json response
            docs_data_list = json_response["results"]["documents"]["content"]["documents"]

            # Reconstruct a new list that contains only the fields we want
            processed_docs_data = [
                {
                    "_id": doc["id"],
                    "file_name": f"{doc["id"]}.pdf",
                    "file_path": os.path.join(sanitize_filename(SCRIBD_SEARCH_TERM), f"{doc["id"]}.pdf"),
                    "file_type": "pdf",
                    "title": doc["title"],
                    "url": doc["reader_url"],
                    "pages": doc["pageCount"],
                    "views": doc["views"],
                    "creation_date": datetime.now(UTC)
                } for doc in docs_data_list
            ]

            # Return the processed docs data list, the total number of parsable pages and the current API page
            return processed_docs_data, json_response["page_count"], json_response["current_page"]


        def pdf_downloader(doc_data: dict, chrome_driver: webdriver.Chrome):
            """Downloads the PDF document using the chrome driver"""
            _id = doc_data["_id"]
            title = doc_data["title"]
            file_name = doc_data["file_name"]

            # Get the pdf display page using https://ilide.info/
            chrome_driver.get(
                parameterized_url_generator(
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
            iframes = chrome_driver.find_elements(By.TAG_NAME, "iframe")

            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and src.startswith("https://ilide.info/viewer/web/viewer.html?file="):
                    pdf_viewer_page_url = src
                    break

            # Redirect to the pdf viewer page
            log_message(f"PDFs Downloading | Redirecting to {pdf_viewer_page_url}")
            chrome_driver.get(pdf_viewer_page_url)

            # Click on the download button
            download_button = WebDriverWait(chrome_driver, 5).until(EC.element_to_be_clickable((By.ID, "download")))
            download_button.click()

            # Extract the original download filename from the pdf viewer page URL
            decoded_pdf_viewer_page_url = unquote(pdf_viewer_page_url)
            download_filename = re.search(
                r"https://ilide\.info/docdownloadv2-([^?]+)",
                decoded_pdf_viewer_page_url
            ).group(1)

            if download_filename:  # Only rename the downloaded file if the original filename was extracted successfully
                download_filename = f"ilide.info-{download_filename}.pdf"
                log_message(f"PDFs Downloading | Extracted download filename : {download_filename}")

                # Wait for file download to complete
                while download_filename not in os.listdir(DOWNLOAD_PATH):
                    log_message("PDFs Downloading | File not found yet, waiting...")
                    time.sleep(5)  # Check every 5 seconds

                # Rename the newly downloaded file
                rename_file(os.path.join(DOWNLOAD_PATH, download_filename), os.path.join(DOWNLOAD_PATH, file_name))
                log_message(f"PDFs Downloading | Renamed file '{download_filename}' to '{file_name}'")


        def scrap_data_and_download_pdfs():
            """Scrape data and download PDFs"""
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
                log_message(f"input: {subcategory}")  # Log the input value
                pdf_downloader(doc, driver)
            driver.quit()

        # Execute the scraping and download process
        scrap_data_and_download_pdfs()
