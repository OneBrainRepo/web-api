from mongoengine import connect
import os

# All other related configurations
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME","DEMO")
MONGODB_CONNECTION_ADDRESS=os.getenv("MONGODB_CONNECTION_ADDRESS","localhost:27017")
# Do NOT TOUCH BELOW
MONGODB_HOST = f"mongodb://{MONGODB_CONNECTION_ADDRESS}/{MONGODB_DB_NAME}"
connect(MONGODB_DB_NAME, host=MONGODB_HOST)