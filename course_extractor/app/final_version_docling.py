import os
from dotenv import load_dotenv
import logging
import time
from pathlib import Path
import pymongo
import tempfile
import hashlib
from datetime import datetime

# Import des modules Docling
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Définir les constantes globales

PDF_PATH = os.getenv("DOWNLOAD_PATH") # Répertoire contenant les PDFs
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")





2
def connect_to_mongodb():
    """Établit une connexion à la base de données MongoDB."""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logger.info(f"Connexion réussie à MongoDB: {DB_NAME}.{COLLECTION_NAME}")
        return collection
    except Exception as e:
        logger.error(f"Erreur de connexion à MongoDB: {e}")
        raise


def process_pdf(pdf_path, collection):
    """Traite un fichier PDF et stocke uniquement le contenu textuel dans MongoDB."""
    try:
        # Vérifier si le document existe déjà
        file_name = os.path.basename(pdf_path)
        existing_doc = collection.find_one({"file_name": file_name})

        if existing_doc:
            logger.info(f"Le document {file_name} existe déjà dans la collection. Ignoré.")
            return False

        # Calcul du hachage SHA-256 pour le fichier
        file_hash = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
        file_hash_str = file_hash.hexdigest()

        # Création d'un répertoire temporaire
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialisation du convertisseur de document
            doc_converter = DocumentConverter()

            start_time = time.time()

            # Conversion du document
            logger.info(f"Extraction du texte depuis: {pdf_path}")
            conv_result = doc_converter.convert(pdf_path)
            document = conv_result.document

            # Extraction du nom de base du fichier
            doc_filename = Path(pdf_path).stem

            # Sauvegarde du fichier Markdown
            md_filepath = temp_path / f"{doc_filename}.md"
            document.save_as_markdown(md_filepath)

            # Lecture du contenu Markdown
            with open(md_filepath, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # Extraire le titre
            title = document.title if hasattr(document, 'title') and document.title else doc_filename

            end_time = time.time() - start_time
            logger.info(f"Extraction terminée en {end_time:.2f} secondes")

            # Préparation du document pour MongoDB
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

            # Insertion dans MongoDB
            collection.insert_one(mongo_doc)
            logger.info(f"Document {file_name} traité et stocké avec succès")
            return True

    except Exception as e:
        logger.error(f"Erreur lors du traitement de {pdf_path}: {e}")
        return False


def main():
    """Fonction principale."""
    # Connexion à MongoDB
    collection = connect_to_mongodb()

    # Création d'index de base
    collection.create_index("file_name")
    collection.create_index("file_hash")

    # Vérifier si PDF_PATH est un fichier ou un répertoire
    path = Path(PDF_PATH)

    if path.is_file() and path.suffix.lower() == '.pdf':
        # Traiter un seul fichier PDF
        logger.info(f"Traitement du fichier: {path}")
        process_pdf(str(path), collection)
    elif path.is_dir():
        # Traiter tous les PDF dans le répertoire
        pdf_files = list(path.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"Aucun fichier PDF trouvé dans {path}")
            return

        total_files = len(pdf_files)
        processed_files = 0

        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"Traitement du fichier {i}/{total_files}: {pdf_file}")

            if process_pdf(str(pdf_file), collection):
                processed_files += 1

        logger.info(f"Traitement terminé. {processed_files}/{total_files} fichiers traités avec succès.")
    else:
        logger.error(f"Le chemin spécifié n'est pas valide: {PDF_PATH}")
        return


if __name__ == "__main__":
    main()