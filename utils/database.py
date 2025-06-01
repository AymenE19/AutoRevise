from datetime import datetime, UTC

from bson import ObjectId
from pymongo import MongoClient

from utils.logger import setup_logger

# Logging Configuration
logger = setup_logger()


class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.topic = None

    def select_topic(self, topic_name: str):
        self.topic = self.db[topic_name]

    def get_all_topics(self) -> list:
        return self.db.list_collection_names()

    def delete_topic(self, topic_name: str) -> bool:
        self.db[topic_name].drop()
        return True

    def insert_session(self, session_data: dict) -> ObjectId:
        session_data["created_at"] = datetime.now(UTC)
        return self.topic.insert_one(session_data).inserted_id

    def get_session(self, session_id: str) -> dict:
        return self.topic.find_one({"_id": ObjectId(session_id)})

    def get_all_sessions(self, sort_by_order: bool = True) -> list:
        cursor = self.topic.find()
        if sort_by_order:
            cursor = cursor.sort("session_order", 1)
        return list(cursor)

    def update_session(self, session_id: str, updates: dict) -> bool:
        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": updates}
        )
        return result.modified_count > 0

    def delete_session(self, session_id: str) -> bool:
        result = self.topic.delete_one({"_id": ObjectId(session_id)})
        return result.deleted_count > 0

    def close(self):
        self.client.close()
