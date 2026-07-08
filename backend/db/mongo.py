# Import the MongoClient class from the pymongo library to connect to MongoDB
from pymongo import MongoClient

# Define the MongoDB connection URI — MongoDB is running locally on the default port 27017
MONGO_URI = "mongodb://localhost:27017/"

# Define the name of the database where all honeypot data will be stored
DB_NAME = "honeypot"

# Define the name of the collection (analogous to a SQL table) that stores attack records
COLLECTION_NAME = "attacks"

# Create a MongoClient instance using the URI — this establishes the connection to MongoDB
_client = MongoClient(MONGO_URI)

# Access the 'honeypot' database from the connected MongoDB client
_db = _client[DB_NAME]


# Define a function that returns the 'attacks' collection — called by other modules to interact with the DB
def get_collection():
    # Return the attacks collection object — callers can use this to insert, find, or update documents
    return _db[COLLECTION_NAME]
