# import os
# import subprocess
# import json
# from pathlib import Path
# from dotenv import load_dotenv
#
# from AutoRevise.course_extractor.app.scraper.scraper import scrap_data_and_download_pdfs
# from AutoRevise.course_extractor.app.storage.database import AtlasClient
# from AutoRevise.course_extractor.app.storage.models import CourseDocument
# from AutoRevise.course_extractor.app.utils.logging import log_message
#
#
# def main():
#     # Charger les variables d'environnement
#     load_dotenv()
#
#     # Définir les constantes globales
#     DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
#     MONGODB_URI = os.getenv("MONGODB_URI")
#     MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
#     MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
#
#     # Vérifier les chemins et configurations
#     if not DOWNLOAD_PATH:
#         print("Erreur: DOWNLOAD_PATH non défini dans .env")
#         return
#
#     os.makedirs(DOWNLOAD_PATH, exist_ok=True)
#
#     if not all([MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME]):
#         print("Erreur: Configuration MongoDB incomplète. Vérifiez votre fichier .env")
#         return
#
#     # Initialiser le client MongoDB
#     mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)
#
#     # Étape 1: Scraping et téléchargement des PDFs
#     print("\n=== ÉTAPE 1: SCRAPING ET TÉLÉCHARGEMENT ===\n")
#     scrap_data_and_download_pdfs()
#
#     # Étape 2: Extraction avec Marker et mise à jour des documents MongoDB
#     print("\n=== ÉTAPE 2: EXTRACTION AVEC MARKER ===\n")
#
#     # Trouver tous les PDFs
#     pdfs_to_process = []
#     for root, _, files in os.walk(DOWNLOAD_PATH):
#         for file in files:
#             if file.lower().endswith('.pdf'):
#                 pdfs_to_process.append(os.path.join(root, file))
#
#     print(f"Trouvé {len(pdfs_to_process)} fichiers PDF à traiter")
#
#     # Traiter chaque PDF avec Marker directement
#     success_count = 0
#     error_count = 0
#
#     for pdf_path in pdfs_to_process:
#         relative_path = os.path.relpath(pdf_path, DOWNLOAD_PATH)
#         file_name = os.path.basename(pdf_path)
#         doc_id = Path(file_name).stem  # Nom du fichier sans extension
#
#         print(f"Traitement de {relative_path}...")
#
#         # Vérifier si le document existe dans MongoDB ou le créer
#         existing_doc = mongodb_client.get_one(MONGODB_COLLECTION_NAME, {"_id": doc_id})
#         if not existing_doc:
#             doc_data = {
#                 "_id": doc_id,
#                 "file_name": file_name,
#                 "file_path": relative_path,
#                 "file_type": "pdf",
#                 "title": doc_id.replace('_', ' ').title(),
#             }
#             mongodb_client.insert_one(MONGODB_COLLECTION_NAME, doc_data, ignore_duplicates=True)
#
#         # Créer le dossier de sortie pour Marker
#         output_dir = os.path.join(os.path.dirname(pdf_path), f"{Path(pdf_path).stem}_marker_output")
#         os.makedirs(output_dir, exist_ok=True)
#
#         # Exécuter Marker directement
#         try:
#             marker_cmd = ["marker_single", pdf_path, "--output_format", "markdown", "--output_dir", output_dir]
#             print(f"Exécution de: {' '.join(marker_cmd)}")
#
#             # Exécuter Marker directement
#             result = subprocess.run(marker_cmd, capture_output=True, text=True)
#
#             if result.returncode != 0:
#                 print(f"Erreur Marker: {result.stderr}")
#                 error_count += 1
#                 continue
#
#             # Récupérer le fichier markdown
#             markdown_file = os.path.join(output_dir, f"{Path(pdf_path).stem}.md")
#
#             if not os.path.exists(markdown_file):
#                 print(f"Fichier markdown non trouvé: {markdown_file}")
#                 error_count += 1
#                 continue
#
#             # Lire le contenu extrait
#             with open(markdown_file, 'r', encoding='utf-8') as f:
#                 content = f.read()
#
#             # Vérifier si des images ont été extraites
#             images_dir = os.path.join(output_dir, f"{Path(pdf_path).stem}_images")
#             has_images = False
#             if os.path.exists(images_dir):
#                 image_files = [f for f in os.listdir(images_dir) if
#                                f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
#                 has_images = len(image_files) > 0
#
#             # Mettre à jour le document dans MongoDB
#             update_data = {
#                 "content": content,
#                 "content_format": "markdown",
#                 "has_images": has_images,
#                 "images_dir": images_dir if has_images else None
#             }
#
#             mongodb_client.update_one(MONGODB_COLLECTION_NAME, doc_id, update_data)
#             print(f"Document {doc_id} mis à jour avec succès")
#             success_count += 1
#
#         except Exception as e:
#             print(f"Erreur lors du traitement de {file_name}: {str(e)}")
#             error_count += 1
#
#     print(f"\n=== TRAITEMENT TERMINÉ ===")
#     print(f"Succès: {success_count}, Erreurs: {error_count}")
#
#
# if __name__ == "__main__":
#     main()

import os
from dotenv import load_dotenv
import logging
import time
from pathlib import Path
import pymongo
import tempfile
import hashlib
from datetime import datetime
from tqdm import tqdm

# from course_extractor.app.scraper.scraper import scrap_data_and_download_pdfs
# from course_extractor.app.storage.database import AtlasClient
# from course_extractor.app.storage.models import CourseDocument
# from course_extractor.app.utils.logging import log_message


# Import des modules Docling
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration MongoDB
MONGO_URI = "mongodb+srv://mdj:V7Drp2_Fhda9drt@mdj.8ji4o.mongodb.net/?retryWrites=true&w=majority&appName=MDJ"
DB_NAME = "courses_db"
COLLECTION_NAME = "Bases_de_données"

# Charger les variables d'environnement
load_dotenv()

 # Définir les constantes globales

PDF_PATH = os.getenv("DOWNLOAD_PATH") # Répertoire contenant les PDFs
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")


def connect_to_mongodb():
    """Établit une connexion à la base de données MongoDB."""
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logger.info(f"Connexion réussie à MongoDB: {DB_NAME}.{COLLECTION_NAME}")
        return collection
    except Exception as e:
        logger.error(f"Erreur de connexion à MongoDB: {e}")
        raise

def process_pdf(pdf_path, collection):
    """Traite un fichier PDF et stocke uniquement le contenu textuel dans MongoDB + sauvegarde locale."""
    try:
        # Étape 1: Vérifier si le document a déjà été traité
        file_name = os.path.basename(pdf_path)
        existing_doc = collection.find_one({"file_name": file_name})

        if existing_doc:
            logger.info(f"Le document {file_name} existe déjà dans la collection. Ignoré.")
            return False

        # Étape 2: Calcul du hachage SHA-256 pour vérifier l'unicité du contenu
        file_hash = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
        file_hash_str = file_hash.hexdigest()

        # Étape 3: Création d'un répertoire temporaire pour conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Étape 4: Initialisation du convertisseur Docling
            doc_converter = DocumentConverter()

            start_time = time.time()

            # Étape 5: Conversion du fichier PDF
            logger.info(f"Extraction du texte depuis: {pdf_path}")
            conv_result = doc_converter.convert(pdf_path)
            document = conv_result.document

            # Étape 6: Nom du fichier sans extension
            doc_filename = Path(pdf_path).stem

            # Étape 7: Dossier de sortie permanent pour Markdown et images
            output_dir = Path(PDF_PATH) / doc_filename
            output_dir.mkdir(parents=True, exist_ok=True)

            # Étape 8: Sauvegarde du Markdown dans le dossier dédié
            md_filepath = output_dir / f"{doc_filename}.md"
            document.save_as_markdown(md_filepath)

            # Étape 9: Copie des images extraites dans le dossier
            for image_path in temp_path.glob("*.png"):
                dest_image_path = output_dir / image_path.name
                image_path.replace(dest_image_path)

            # Étape 10: Lecture du Markdown
            with open(md_filepath, "r", encoding="utf-8", errors="ignore") as f:
                markdown_content = f.read()

            # Étape 11: Extraction du titre du document
            title = document.title if hasattr(document, 'title') and document.title else doc_filename

            end_time = time.time() - start_time
            logger.info(f"Extraction terminée en {end_time:.2f} secondes")

            # Étape 12: Préparation des données pour MongoDB
            mongo_doc = {
                "file_name": file_name,
                "file_path": str(pdf_path),
                "file_hash": file_hash_str,
                "content_markdown": markdown_content,
                "metadata": {
                    "title": title,
                    "processed_at": datetime.now()
                }
            }

            # Étape 13: Insertion dans MongoDB
            collection.insert_one(mongo_doc)
            logger.info(f"Document {file_name} traité et stocké avec succès dans MongoDB")
            return True

    except Exception as e:
        logger.error(f"Erreur lors du traitement de {pdf_path}: {e}")
        return False



def main():

    #  Scraping et téléchargement des PDFs
    #     print("\n SCRAPING ET TÉLÉCHARGEMENT ===\n")
    #     scrap_data_and_download_pdfs()

    """Fonction principale qui orchestre le traitement des fichiers PDF."""
    # Connexion à MongoDB
    collection = connect_to_mongodb()

    # Création d'index pour accélérer les requêtes
    collection.create_index("file_name")
    collection.create_index("file_hash")

    # Vérification du chemin
    path = Path(PDF_PATH)

    if path.is_file() and path.suffix.lower() == '.pdf':
        # Traitement d’un seul fichier PDF
        logger.info(f"Traitement du fichier: {path}")
        process_pdf(str(path), collection)
    elif path.is_dir():
        # Traitement récursif de tous les fichiers PDF dans le dossier
        pdf_files = list(path.rglob("*.pdf"))

        if not pdf_files:
            logger.warning(f"Aucun fichier PDF trouvé dans {path}")
            return

        total_files = len(pdf_files)
        processed_files = 0

        # Utilisation de tqdm pour afficher une barre de progression avec les options demandées
        for pdf_file in tqdm(pdf_files, total=total_files, desc="Analyse", unit="document", colour="green",
                             dynamic_ncols=True):
            if process_pdf(str(pdf_file), collection):
                processed_files += 1

        logger.info(f"Traitement terminé. {processed_files}/{total_files} fichiers traités avec succès.")
    else:
        logger.error(f"Le chemin spécifié n'est pas valide: {PDF_PATH}")
        return

if __name__ == "__main__":
    main()
