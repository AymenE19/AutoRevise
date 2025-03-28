import os
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

from AutoRevise.course_extractor.app.scraper.scraper import scrap_data_and_download_pdfs
from AutoRevise.course_extractor.app.storage.database import AtlasClient
from AutoRevise.course_extractor.app.storage.models import CourseDocument
from AutoRevise.course_extractor.app.utils.logging import log_message


def main():
    # Charger les variables d'environnement
    load_dotenv()

    # Définir les constantes globales
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
    MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

    # Vérifier les chemins et configurations
    if not DOWNLOAD_PATH:
        print("Erreur: DOWNLOAD_PATH non défini dans .env")
        return

    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    if not all([MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME]):
        print("Erreur: Configuration MongoDB incomplète. Vérifiez votre fichier .env")
        return

    # Initialiser le client MongoDB
    mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)

    # Étape 1: Scraping et téléchargement des PDFs
    print("\n=== ÉTAPE 1: SCRAPING ET TÉLÉCHARGEMENT ===\n")
    scrap_data_and_download_pdfs()

    # Étape 2: Extraction avec Marker et mise à jour des documents MongoDB
    print("\n=== ÉTAPE 2: EXTRACTION AVEC MARKER ===\n")

    # Trouver tous les PDFs
    pdfs_to_process = []
    for root, _, files in os.walk(DOWNLOAD_PATH):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdfs_to_process.append(os.path.join(root, file))

    print(f"Trouvé {len(pdfs_to_process)} fichiers PDF à traiter")

    # Traiter chaque PDF avec Marker directement
    success_count = 0
    error_count = 0

    for pdf_path in pdfs_to_process:
        relative_path = os.path.relpath(pdf_path, DOWNLOAD_PATH)
        file_name = os.path.basename(pdf_path)
        doc_id = Path(file_name).stem  # Nom du fichier sans extension

        print(f"Traitement de {relative_path}...")

        # Vérifier si le document existe dans MongoDB ou le créer
        existing_doc = mongodb_client.get_one(MONGODB_COLLECTION_NAME, {"_id": doc_id})
        if not existing_doc:
            doc_data = {
                "_id": doc_id,
                "file_name": file_name,
                "file_path": relative_path,
                "file_type": "pdf",
                "title": doc_id.replace('_', ' ').title(),
            }
            mongodb_client.insert_one(MONGODB_COLLECTION_NAME, doc_data, ignore_duplicates=True)

        # Créer le dossier de sortie pour Marker
        output_dir = os.path.join(os.path.dirname(pdf_path), f"{Path(pdf_path).stem}_marker_output")
        os.makedirs(output_dir, exist_ok=True)

        # Exécuter Marker directement
        try:
            marker_cmd = ["marker_single", pdf_path, "--output_format", "markdown", "--output_dir", output_dir]
            print(f"Exécution de: {' '.join(marker_cmd)}")

            # Exécuter Marker directement
            result = subprocess.run(marker_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Erreur Marker: {result.stderr}")
                error_count += 1
                continue

            # Récupérer le fichier markdown
            markdown_file = os.path.join(output_dir, f"{Path(pdf_path).stem}.md")

            if not os.path.exists(markdown_file):
                print(f"Fichier markdown non trouvé: {markdown_file}")
                error_count += 1
                continue

            # Lire le contenu extrait
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Vérifier si des images ont été extraites
            images_dir = os.path.join(output_dir, f"{Path(pdf_path).stem}_images")
            has_images = False
            if os.path.exists(images_dir):
                image_files = [f for f in os.listdir(images_dir) if
                               f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                has_images = len(image_files) > 0

            # Mettre à jour le document dans MongoDB
            update_data = {
                "content": content,
                "content_format": "markdown",
                "has_images": has_images,
                "images_dir": images_dir if has_images else None
            }

            mongodb_client.update_one(MONGODB_COLLECTION_NAME, doc_id, update_data)
            print(f"Document {doc_id} mis à jour avec succès")
            success_count += 1

        except Exception as e:
            print(f"Erreur lors du traitement de {file_name}: {str(e)}")
            error_count += 1

    print(f"\n=== TRAITEMENT TERMINÉ ===")
    print(f"Succès: {success_count}, Erreurs: {error_count}")


if __name__ == "__main__":
    main()