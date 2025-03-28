from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, BulkWriteError

from AutoRevise.course_extractor.app.utils.logging import log_message


class AtlasClient:
    def __init__(self, db_uri: str, db_name: str):
        self.mongodb_client = MongoClient(db_uri)
        self.db = self.mongodb_client[db_name]

    def ping(self):
        return self.mongodb_client.admin.command('ping')

    def insert_one(self, collection_name: str, item: dict, ignore_duplicates: bool = False):
        """
        Insère un document dans la collection spécifiée.

        Args:
            collection_name (str): Nom de la collection
            item (dict): Document à insérer
            ignore_duplicates (bool): Si True, ignore les erreurs de duplication

        Returns:
            L'ID du document inséré, ou None en cas d'erreur
        """
        try:
            return self.db[collection_name].insert_one(item).inserted_id
        except DuplicateKeyError as e:
            if ignore_duplicates:
                log_message(f"Ignoré: Document avec ID {item.get('_id')} existe déjà")
                return item.get('_id')
            else:
                raise e

    def get_one(self, collection_name: str, _filter: dict = None) -> dict:
        """
        Récupère un document de la collection.

        Args:
            collection_name (str): Nom de la collection
            _filter (dict): Filtre de recherche

        Returns:
            Le document trouvé ou None
        """
        return self.db[collection_name].find_one(filter=_filter)

    def insert_many(self, collection_name: str, items: list[dict], ignore_duplicates: bool = False):
        """
        Insère plusieurs documents dans la collection.

        Args:
            collection_name (str): Nom de la collection
            items (list[dict]): Liste de documents à insérer
            ignore_duplicates (bool): Si True, continue l'insertion malgré les doublons

        Returns:
            Liste des IDs insérés, ou liste vide en cas d'erreur
        """
        if not items:
            return []

        try:
            result = self.db[collection_name].insert_many(items, ordered=not ignore_duplicates)
            return result.inserted_ids
        except BulkWriteError as e:
            if ignore_duplicates:
                # Extraction des documents correctement insérés
                successful_ids = []
                for doc in items:
                    try:
                        # Vérifier si le document existe déjà
                        existing = self.get_one(collection_name, {"_id": doc["_id"]})
                        if not existing:
                            # Si n'existe pas, essayer d'insérer individuellement
                            result = self.insert_one(collection_name, doc, ignore_duplicates=True)
                            if result:
                                successful_ids.append(result)
                    except Exception as inner_e:
                        log_message(f"Erreur lors de l'insertion du document {doc.get('_id')}: {str(inner_e)}")

                log_message(
                    f"Insertion par lots partiellement réussie: {len(successful_ids)}/{len(items)} documents insérés")
                return successful_ids
            else:
                raise e

    def get_many(self, collection_name: str, _filter: dict = None, limit: int = 0) -> list[dict]:
        """
        Récupère plusieurs documents de la collection.

        Args:
            collection_name (str): Nom de la collection
            _filter (dict): Filtre de recherche
            limit (int): Nombre maximum de documents à retourner (0 = pas de limite)

        Returns:
            Liste des documents trouvés
        """
        return list(self.db[collection_name].find(filter=_filter, limit=limit))

    def update_one(self, collection_name: str, item_id: str, new_data: dict):
        """
        Met à jour un document dans la collection.

        Args:
            collection_name (str): Nom de la collection
            item_id: ID du document à mettre à jour
            new_data (dict): Nouvelles données

        Returns:
            Résultat de la mise à jour
        """
        result = self.db[collection_name].update_one({'_id': item_id}, {'$set': new_data}, upsert=True)

        if result.modified_count > 0:
            log_message(f"Document {item_id} mis à jour avec succès.")
        elif result.upserted_id:
            log_message(f"Document {item_id} créé avec succès.")
        else:
            log_message(f"Aucune modification pour le document {item_id}.")

        return result

    def update_many(self, collection_name: str, filter_dict: dict, new_data: dict):
        """
        Met à jour plusieurs documents dans la collection.

        Args:
            collection_name (str): Nom de la collection
            filter_dict (dict): Filtre pour sélectionner les documents
            new_data (dict): Nouvelles données

        Returns:
            Résultat de la mise à jour
        """
        result = self.db[collection_name].update_many(filter_dict, {'$set': new_data})

        log_message(f"{result.modified_count} documents mis à jour.")
        return result