from os import getenv

from dotenv import load_dotenv

# --- Constants and Configuration ---
load_dotenv("../.env")  # Load environment variables once at the beginning

MONGODB_URI = getenv("MONGODB_URI")
MONGODB_DB_NAME = getenv("MONGODB_DB_NAME")

GEMINI_API_KEY = getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = getenv("GEMINI_MODEL_NAME")

MARKDOWNS_ROOT_FOLDER = getenv("MARKDOWNS_ROOT_FOLDER")
