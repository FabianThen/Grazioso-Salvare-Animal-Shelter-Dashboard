"""
AnimalShelter CRUD module — enhanced version.

Enhancements applied for CS 499 Milestone Four (Databases), based on
the findings from the Milestone One code review:

1. Removed corrupted content: the original file had a stray shell
   heredoc command ("EOFcat > .env.example << 'EOF'" followed by the
   contents of .env.example) appended after the read() method, which
   made the module impossible to import without a SyntaxError.
2. Completed the CRUD contract: the class docstring promised full CRUD
   operations, but the original only implemented create() and read().
   update() and delete() are now implemented.
3. URL-encoded the credentials: the original interpolated the username
   and password directly into the MongoDB URI with an f-string, which
   breaks whenever either value contains a reserved character such as
   @, :, or /. Both are now escaped with urllib.parse.quote_plus
   before being placed in the connection string.
4. Added consistent connection guards: the original read() checked
   `if self.collection is None` before querying, but create() did not,
   so a failed connection would crash create() with an AttributeError
   instead of failing gracefully. Every method now performs the same
   guard through a single helper.
5. Added indexing: the dashboard filters frequently on animal type,
   breed, and rescue-outcome fields, so indexes are created on those
   fields at connection time to keep those queries efficient as the
   collection grows.
"""

import os
from urllib.parse import quote_plus

from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError


class AnimalShelter(object):
    """CRUD operations for the Animal collection in MongoDB."""

    # Fields the Grazioso Salvare dashboard filters on most often.
    # Indexing these keeps those lookups efficient as the collection grows.
    INDEXED_FIELDS = ["animal_type", "breed", "outcome_type"]

    def __init__(self):
        # Connection variables read from the environment, with local
        # development defaults.
        user = os.environ.get('MONGO_USER', 'aacuser')
        password = os.environ.get('MONGO_PASS', '')
        host = os.environ.get('MONGO_HOST', 'localhost')
        port = int(os.environ.get('MONGO_PORT', 27017))
        db = os.environ.get('MONGO_DB', 'aac')
        col = os.environ.get('MONGO_COL', 'animals')

        try:
            # quote_plus escapes reserved characters (@, :, /, etc.) so
            # a password containing them does not corrupt the URI.
            safe_user = quote_plus(user)
            safe_password = quote_plus(password)

            self.client = MongoClient(
                f'mongodb://{safe_user}:{safe_password}@{host}:{port}',
                authSource=db,
                authMechanism='SCRAM-SHA-1'
            )
            self.database = self.client[db]
            self.collection = self.database[col]

            # Verify the connection by listing collection names.
            self.database.list_collection_names()

            # Create indexes on the fields the dashboard queries most.
            self._ensure_indexes()

            print("Connected to MongoDB successfully.")

        except PyMongoError as e:
            print(f"Could not connect to MongoDB: {e}")
            self.client = None
            self.database = None
            self.collection = None

    def _ensure_indexes(self):
        """Creates ascending indexes on frequently queried fields (idempotent)."""
        for field in self.INDEXED_FIELDS:
            self.collection.create_index([(field, ASCENDING)])

    def _has_collection(self, operation):
        """Returns True if a collection is available; logs and returns False otherwise."""
        if self.collection is None:
            print(f"No collection available for {operation}.")
            return False
        return True

    def create(self, data):
        """
        Inserts a single document into the animals collection.
        :param data: dict representing the document to insert
        :return: True if the insert succeeded, else False
        """
        if data is None:
            raise Exception("Nothing to save, data parameter is empty")
        if not self._has_collection("insert"):
            return False

        try:
            self.collection.insert_one(data)
            return True
        except PyMongoError as e:
            print(f"Error inserting data: {e}")
            return False

    def read(self, query):
        """
        Finds documents in the animals collection that match the query.
        :param query: dict representing the search filter
        :return: list of matching documents; empty list if none or on error
        """
        if not self._has_collection("queries"):
            return []

        try:
            return list(self.collection.find(query))
        except PyMongoError as e:
            print(f"Error querying data: {e}")
            return []

    def update(self, query, new_values):
        """
        Updates all documents matching the query.
        :param query: dict representing the documents to match
        :param new_values: dict of fields/values to set
        :return: the number of documents modified (0 on error or no match)
        """
        if query is None or new_values is None:
            raise Exception("update requires both a query and new values")
        if not self._has_collection("update"):
            return 0

        try:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError as e:
            print(f"Error updating data: {e}")
            return 0

    def delete(self, query):
        """
        Deletes all documents matching the query.
        :param query: dict representing the documents to remove
        :return: the number of documents deleted (0 on error or no match)
        """
        if query is None:
            raise Exception("delete requires a query")
        if not self._has_collection("delete"):
            return 0

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Error deleting data: {e}")
            return 0
