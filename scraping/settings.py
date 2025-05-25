from os import getenv

from dotenv import load_dotenv

# --- Constants and Configuration ---
load_dotenv("../.env")  # Load environment variables once at the beginning


# Scribd Setup
SCRIBD_API_BASE_URL = getenv("SCRIBD_API_BASE_URL")
SCRIBD_MAX_PARSABLE_PAGES = int(getenv("SCRIBD_MAX_PARSABLE_PAGES"))
SCRIBD_MAX_SAVED_RESULTS = int(getenv("SCRIBD_MAX_SAVED_RESULTS"))
SCRIBD_LANGS = getenv("SCRIBD_LANGS").split(",")
SCRIBD_FILE_TYPES = getenv("SCRIBD_FILE_TYPES").split(",")
SCRIBD_PREFERRED_FILE_LENGTH = getenv("SCRIBD_PREFERRED_FILE_LENGTH")
SCRIBD_MIN_FILE_LENGTH = int(getenv("SCRIBD_MIN_FILE_LENGTH"))
SCRIBD_MAX_FILE_LENGTH = int(getenv("SCRIBD_MAX_FILE_LENGTH"))

# PDF download path
SCRAPING_ROOT_DOWNLOAD_PATH = getenv("SCRAPING_ROOT_DOWNLOAD_PATH")
