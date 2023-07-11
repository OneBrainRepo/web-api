from mongoengine import connect
import os

# All other related configurations
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME","DEMO")
MONGODB_CONNECTION_ADDRESS=os.getenv("MONGODB_CONNECTION_ADDRESS","mongo_db:27017")
MONGODB_DB_USERNAME=os.getenv("MONGODB_DB_USERNAME","root")
MONGODB_DB_PASSWD=os.getenv("MONGODB_DB_PASSWD","example")
# Do NOT TOUCH BELOW
MONGODB_HOST, MONGODB_PORT = MONGODB_CONNECTION_ADDRESS.split(':')

print(f"MongoDB host address : {MONGODB_HOST}")
connect(db=MONGODB_DB_NAME, host=MONGODB_HOST, port=int(MONGODB_PORT), username=MONGODB_DB_USERNAME, password=MONGODB_DB_PASSWD, retryWrites=False)
# MONGODB_HOST = f"mongodb://{MONGODB_DB_USERNAME}:{MONGODB_DB_PASSWD}@{MONGODB_CONNECTION_ADDRESS}"
# print(f"MongoDB host address : {MONGODB_HOST}")
# connect(MONGODB_DB_NAME, host=MONGODB_HOST)