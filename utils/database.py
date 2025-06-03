from datetime import datetime, UTC

from bson import ObjectId
from pymongo import MongoClient

from utils.logger import setup_logger

# Logging Configuration
logger = setup_logger()


class MongoDB:
    def __init__(self, uri: str, db_name: str):
        """Connect to the MongoDB database using the provided URI and database name."""

        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.topic = None

        # Logging
        logger.info(f"Connected to MongoDB database: {db_name}")

    def __enter__(self):
        """ Return self to be used inside the with block """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """ Ensure client is closed when exiting the with block """
        self.close()

    def select_topic(self, topic_name: str):
        """ Select a collection (topic) to work with. """

        self.topic = self.db[topic_name]

        # Logging
        logger.info(f"Selected topic: {topic_name}")

    def get_all_topics(self) -> list:
        """ List all collection names in the database. """

        topics = self.db.list_collection_names()

        # Logging
        logger.info("Fetched all topics.")

        return topics

    def find_topic_by_name(self, name: str) -> bool:
        """Check if a collection with the given name exists in the database."""

        exists = name in self.db.list_collection_names()

        # Logging
        logger.info(f"Collection '{name}' exists: {exists}")

        return exists

    def delete_topic(self, topic_name: str) -> bool:
        """ Delete a collection from the database. """

        self.db[topic_name].drop()

        # Logging
        logger.info(f"Deleted topic: {topic_name}")

        return True

    def insert_session(self, session_data: dict) -> ObjectId:
        """ Insert a session document into the selected topic with a timestamp. """

        session_data["created_at"] = datetime.now(UTC)
        inserted_id = self.topic.insert_one(session_data).inserted_id

        # Logging
        logger.info(f"Inserted session with ID: {inserted_id}")

        return inserted_id

    def get_session(self, session_id: str) -> dict:
        """ Retrieve a session document by its ID. """

        session = self.topic.find_one({"_id": ObjectId(session_id)})

        # Logging
        logger.info(f"Retrieved session with ID: {session_id}")

        return session

    def get_all_sessions(self, sort_by_order: bool = True) -> list:
        """ Retrieve all sessions from the selected topic, optionally sorted by 'session_order'. """

        cursor = self.topic.find()
        if sort_by_order:
            cursor = cursor.sort("session_order", 1)
        sessions = list(cursor)

        # Logging
        logger.info(f"Retrieved all sessions. Sorted: {sort_by_order}")

        return sessions

    def find_session_by_order(self, session_order: int) -> dict | None:
        """Search for a session by its 'session_order' field in the selected topic."""

        session = self.topic.find_one({"session_order": session_order})

        # Logging
        logger.info(f"Searched for session_order '{session_order}'. Found: {bool(session)}")

        return session

    def find_session_by_name(self, session_title: str) -> dict | None:
        """Search for a session by its 'session_title' field in the selected topic."""

        session = self.topic.find_one({"session_title": session_title})

        # Logging
        logger.info(f"Searched for session_title '{session_title}'. Found: {bool(session)}")

        return session

    def update_session(self, session_id: str, updates: dict) -> bool:
        """ Update a session document by ID with the given updates. """

        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": updates}
        )
        success = result.modified_count > 0

        # Logging
        logger.info(f"Updated session {session_id}: Success = {success}")

        return success

    def delete_session(self, session_id: str) -> bool:
        """ Delete a session document by its ID. """

        result = self.topic.delete_one({"_id": ObjectId(session_id)})
        success = result.deleted_count > 0

        # Logging
        logger.info(f"Deleted session {session_id}: Success = {success}")

        return success

    def insert_map_mind(self, session_id: str, map_mind_data: list[dict]) -> bool:
        """ Insert a list of dictionaries into the 'map_mind' field of a session document. """

        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"map_mind": map_mind_data}}
        )
        success = result.modified_count > 0

        # Logging
        logger.info(f"Inserted map_mind for session {session_id}: Success = {success}")

        return success

    def update_map_mind(self, session_id: str, new_map_mind: list[dict]) -> bool:
        """Update the 'map_mind' field of a session document."""

        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"map_mind": new_map_mind}}
        )
        success = result.modified_count > 0

        # Logging
        logger.info(f"Updated map_mind for session {session_id}: Success = {success}")

        return success

    def insert_markdown_content(self, session_id: str, markdowns: list[str]) -> bool:
        """Insert a list of markdown strings into the 'markdown_content' field of a session."""

        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"markdown_content": markdowns}}
        )
        success = result.modified_count > 0

        # Logging
        logger.info(f"Inserted markdown_content for session {session_id}: Success = {success}")

        return success

    def update_markdown_content(self, session_id: str, new_markdowns: list[str]) -> bool:
        """Update the 'markdown_content' field of a session with new markdown data."""

        result = self.topic.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"markdown_content": new_markdowns}}
        )
        success = result.modified_count > 0

        # Logging
        logger.info(f"Updated markdown_content for session {session_id}: Success = {success}")

        return success

    def close(self):
        """ Close the connection to the MongoDB server. """

        if self.client:
            self.client.close()

        # Logging
        logger.info("Closed MongoDB connection.")
