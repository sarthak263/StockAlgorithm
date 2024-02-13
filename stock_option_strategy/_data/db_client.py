from pymongo import MongoClient
from stock_option_strategy.config._settings import get_database_uri
class MongoClientWrapper:
    def __init__(self, connection_string: str, database_name: str = "MyStockDB"):
        """
        Initializes the MongoDB client and selects the specified database.

        :param connection_string: The MongoDB connection string.
        :param database_name: The name of the database to connect to.
        """
        client = MongoClient(connection_string)
        self.db = client[database_name]


DB_Client = MongoClientWrapper(get_database_uri())