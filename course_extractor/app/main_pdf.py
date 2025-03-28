import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Imports pour Marker
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

# Imports pour MongoDB
from AutoRevise.course_extractor.app.storage.database import AtlasClient
from AutoRevise.course_extractor.app.utils.logging import log_message


def extract_and_store_pdfs(pdf_folder, mongodb_client, collection_name, output_format="markdown"):
    """
    Extrait le contenu des PDFs dans un dossier spécifique et stocke les résultats dans MongoDB.

    Args:
        pdf_folder (str): Chemin vers le dossier contenant les PDFs
        mongodb_client (AtlasClient): Client MongoDB initialisé
        collection_name (str): Nom de la collection MongoDB
        output_format (str): Format d'extraction (markdown, html, json)

    Returns:
        tuple: (success_count, error_count) - Nombre de succès et d'échecs
    """
    # Vérifier si le dossier existe
    if not os.path.exists(pdf_folder):
        log_message(f"Erreur: Le dossier {pdf_folder} n'existe pas")
        return 0, 0

    # Initialisation du convertisseur Marker
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
        config={"output_format": output_format}
    )

    # Trouver tous les PDFs dans le dossier
    pdf_files = []
    for file in os.listdir(pdf_folder):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(pdf_folder, file))

    log_message(f"Trouvé {len(pdf_files)} fichiers PDF à traiter dans {pdf_folder}")

    # Traiter chaque PDF
    success_count = 0
    error_count = 0

    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        doc_id = Path(file_name).stem  # Nom du fichier sans extension

        log_message(f"Traitement de {file_name}...")

        # Vérifier si le document existe dans MongoDB ou le créer
        existing_doc = mongodb_client.get_one(collection_name, {"_id": doc_id})
        if not existing_doc:
            doc_data = {
                "_id": doc_id,
                "file_name": file_name,
                "file_path": os.path.relpath(pdf_path, os.getenv("DOWNLOAD_PATH", "")),
                "file_type": "pdf",
                "title": doc_id.replace('_', ' ').title(),
            }
            mongodb_client.insert_one(collection_name, doc_data, ignore_duplicates=True)

        try:
            # Traiter le PDF avec Marker
            rendered = converter(pdf_path)

            # Extraire le texte et les images
            text, _, images = text_from_rendered(rendered)

            # Traitement des images
            has_images = len(images) > 0
            images_dir = None

            if has_images:
                # Créer un dossier pour les images
                images_dir = os.path.join(os.path.dirname(pdf_path), f"{doc_id}_images")
                os.makedirs(images_dir, exist_ok=True)

                # Sauvegarder les images
                for idx, img_data in enumerate(images):
                    img_path = os.path.join(images_dir, f"image_{idx}.png")
                    with open(img_path, 'wb') as f:
                        f.write(img_data)

            # Récupérer le contenu selon le format
            content = text
            if hasattr(rendered, 'markdown'):
                content = rendered.markdown
            elif hasattr(rendered, 'html'):
                content = rendered.html
            elif hasattr(rendered, 'children'):
                # Pour JSON, on stocke l'objet complet
                content = rendered.model_dump()

            # Mettre à jour le document dans MongoDB
            update_data = {
                "content": content,
                "content_format": output_format,
                "has_images": has_images,
                "images_dir": images_dir
            }

            # Ajouter les métadonnées si disponibles
            if hasattr(rendered, 'metadata'):
                update_data["metadata"] = rendered.metadata

            mongodb_client.update_one(collection_name, doc_id, update_data)
            log_message(f"Document {doc_id} mis à jour avec succès")
            success_count += 1

        except Exception as e:
            log_message(f"Erreur lors du traitement de {file_name}: {str(e)}")
            error_count += 1

    log_message(f"Traitement terminé pour {pdf_folder}. Succès: {success_count}, Erreurs: {error_count}")
    return success_count, error_count


def main():
    # Chargement des variables d'environnement
    load_dotenv()

    # Configuration
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
    MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

    # Vérification des configurations
    if not all([DOWNLOAD_PATH, MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME]):
        print("Erreur: Variables d'environnement manquantes. Vérifiez votre fichier .env")
        return

    # Initialisation du client MongoDB
    mongodb_client = AtlasClient(MONGODB_URI, MONGODB_DB_NAME)

    # Chemin vers le dossier des PDFs Python
    python_pdfs_folder = os.path.join(DOWNLOAD_PATH)

    # Appeler la fonction pour extraire et stocker
    success, errors = extract_and_store_pdfs(
        pdf_folder=python_pdfs_folder,
        mongodb_client=mongodb_client,
        collection_name=MONGODB_COLLECTION_NAME,
        output_format="markdown"  # Vous pouvez changer en "html" ou "json"
    )

    print(f"\n=== TRAITEMENT TERMINÉ ===")
    print(f"Total - Succès: {success}, Erreurs: {errors}")


if __name__ == "__main__":
    main()