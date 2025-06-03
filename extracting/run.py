import json
import os

from dotenv import load_dotenv

from extracting.functionalities import (
    convert_multi_pdfs_to_markdowns, extract_headings_from_multi_markdown_files, send_structure_to_gemini,
    enrich_json_with_markdown_only_titles
)
from extracting.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME, MARKDOWNS_ROOT_FOLDER
from scraping.settings import SCRAPING_ROOT_DOWNLOAD_PATH
from utils.files import ensure_directory_exists
from utils.logger import setup_logger

# --- Constants and Configuration ---
load_dotenv("../.env")  # Load environment variables once at the beginning

# Logging Configuration
logger = setup_logger()

# Define the folder paths
INPUT_FOLDER = SCRAPING_ROOT_DOWNLOAD_PATH
OUTPUT_FOLDER = MARKDOWNS_ROOT_FOLDER
ensure_directory_exists(OUTPUT_FOLDER)


def run_extracting():
    # Iterate over all PDF files in the INPUT_FOLDER and its subfolders
    for element in os.listdir(INPUT_FOLDER):

        if os.path.isdir(os.path.join(INPUT_FOLDER, element)):
            # STEP 0 - Convert PDFs into Markdown files -----------------
            topic_pdfs_folder_path = os.path.join(INPUT_FOLDER, element)
            topic_mds_folder_path = os.path.join(OUTPUT_FOLDER, element)
            ensure_directory_exists(topic_mds_folder_path)

            logger.info(
                f"Converting all PDF files in '{topic_pdfs_folder_path}'"
                f" to Markdown and saving them in '{topic_mds_folder_path}...'"
            )

            convert_multi_pdfs_to_markdowns(topic_pdfs_folder_path, topic_mds_folder_path)

            logger.info(
                f"Converted all PDF files in '{topic_pdfs_folder_path}'"
                f" to Markdown and saved them in '{topic_mds_folder_path}'"
            )

            # STEP 1 - Extract headings structure -----------------
            extract_headings_from_multi_markdown_files(topic_mds_folder_path)

    extracted_structure_json_path = r"C:\Users\OUSSAMA MDJ\Downloads\structure.json"
    gemini_output_path = r"C:\Users\OUSSAMA MDJ\Downloads\intilaform.txt"
    enriched_output_path = r"C:\Users\OUSSAMA MDJ\Downloads\enriched_output.json"

    print("\n🛠️ Extracting structure from markdown files...")
    structure = extract_headings_from_multi_markdown_files(markdown_folder_path)
    with open(extracted_structure_json_path, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print("✅ Structure extraction completed.")

    # STEP 2 - Send structure to Gemini
    print("\n🤖 Sending structure to Gemini for categorization...")
    send_structure_to_gemini(GEMINI_API_KEY, GEMINI_MODEL_NAME, extracted_structure_json_path, gemini_output_path)

    # STEP 3 - Enrich categorized structure with markdown content
    print("\n🛠️ Enriching Gemini output with real markdown content...")
    result = enrich_json_with_markdown_only_titles(gemini_output_path, markdown_folder_path)

    # Save enriched result
    with open(enriched_output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("✅ Enrichment complete. Output saved to:", enriched_output_path)

    print("\n🎯 All steps completed successfully!")


if __name__ == "__main__":
    run_extracting()
