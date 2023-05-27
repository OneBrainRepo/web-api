from celery import Celery
from enum import Enum
import redis
import os

REDIS_HOST=os.getenv("REDIS_HOST","localhost")
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