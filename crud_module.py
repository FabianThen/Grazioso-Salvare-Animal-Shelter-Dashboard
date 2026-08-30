import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self):
        # Connection Variables — read from environment, with local defaults for development
        USER = os.environ.get('MONGO_USER', 'aacuser')
        PASS = os.environ.get('MONGO_PASS', '')
        HOST = os.environ.get('MONGO_HOST', 'localhost')
        PORT = int(os.environ.get('MONGO_PORT', 27017))
        DB = os.environ.get('MONGO_DB', 'aac')
        COL = os.environ.get('MONGO_COL', 'animals')

        # Initialize Connection with authentication & authSource
        try:
            self.client = MongoClient(
                f'mongodb://{USER}:{PASS}@{HOST}:{PORT}',
                authSource=DB,
                authMechanism='SCRAM-SHA-1'
            )
            self.database = self.client[DB]
            self.collection = self.database[COL]

            # Verify connection by listing collections
            _ = self.database.list_collection_names()
            print("Connected to MongoDB successfully.")

        except PyMongoError as e:
            print(f"Could not connect to MongoDB: {e}")
            self.client = None
            self.database = None
            self.collection = None

    def create(self, data):
        """
        Inserts a single document into the animals collection.
        :param data: dict representing the document to insert
        :return: True if insert was successful, else False
        """
        if data is not None:
            try:
                self.collection.insert_one(data)
                return True
            except PyMongoError as e:
                print(f"Error inserting data: {e}")
                return False
        else:
            raise Exception("Nothing to save, data parameter is empty")

    def read(self, query):
        """
        Finds documents in animals collection that match the query.
        :param query: dict representing the search filter
        :return: list of matching documents; empty list if none or error.
        """
        if self.collection is None:
            print("No collection available for queries.")
            return []

        try:
            cursor = self.collection.find(query)
            results = list(cursor)
            return results
        except PyMongoError as e:
            print(f"Error querying data: {e}")
            return []
EOFcat > .env.example << 'EOF'
MONGO_USER=aacuser
MONGO_PASS=your_password_here
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=aac
MONGO_COL=animals
