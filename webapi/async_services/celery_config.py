from celery import Celery
from enum import Enum
import redis
import os
import time

REDIS_HOST=os.getenv("REDIS_HOST","redis")
REDIS_PORT=os.getenv("REDIS_PORT","6379")
CELERY_BROKER=os.getenv("CELERY_BROKER","redis://localhost")

# Initialize Celery
celery_app = Celery('tasks', broker=CELERY_BROKER)
redis_connection = redis.Redis(host=REDIS_HOST,port=REDIS_PORT,db=0)

# Keep the channel names dynamic with their client id or something such as 
# Channel name = {ChannelNames.httpx_request.done}_{current_user.uuid}
class ChannelNames(Enum):
    httpx_request_done = "HTTP_DONE"
    gdrive_operations = "GDRIVE_DONE"
    # Fine tuning the answer before responding to the user
    fine_tuned_answer = "FINE_TUNING_DONE"
    keywords_extraction = "KEYWORDS_RESP"
    single_channel_response = "SINGLE_CHANNEL_RESP"


def redis_retrive_message_from_channel(rpub):
   message_redis = None
   while message_redis is None or (isinstance(message_redis, dict) and message_redis.get('type') != 'message'):
        message_redis = rpub.get_message()
        if message_redis and isinstance(message_redis, dict) and message_redis.get('type') == 'message':
            message_redis = message_redis.get('data').decode('utf-8')  # decoding byte string to original string
            print(f"Current message data : {message_redis}")
            return message_redis
        else:
            time.sleep(1)  # sleep for some time before checking again 