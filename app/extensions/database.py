# app/extensions/database.py

import mongoengine
from mongoengine.connection import ConnectionFailure
from pymongo.errors import ConfigurationError

def init_db(app):
    """
    Initializes MongoEngine with application configuration.

    :param app: Flask application instance
    """

    try:
        mongoengine.connect(
            db=app.config.get("MONGO_DBNAME"),
            host=app.config.get("MONGO_URI"),
            username=app.config.get("MONGO_USERNAME"),
            password=app.config.get("MONGO_PASSWORD"),
            authentication_source=app.config.get("MONGO_AUTH_SOURCE", "admin"),
            alias="default"
        )
        app.logger.info("MongoDB connection initialized successfully.")

    except ConnectionFailure as e:
        print(e)
    
    except ConfigurationError as e:
        print(e)
