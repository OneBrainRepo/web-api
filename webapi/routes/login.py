from fastapi import Query, Request, APIRouter
from webapi.firebase.fb_db_services import getDemoUser, createDemoUser
from webapi.firebase.firebase_dto import ConversationHistory, DemoUser

router = APIRouter()
#Define Demo related routes here
"""
Firstly we define demo path here
Then we define normal login path here as well
Later on we will change the path which this router is prefixed as

"""


@router.get("/test")
def getDemoTest()-> dict:
    return {"message": "Hello World"}

@router.get('/login')
async def loginEntry(userDTO : DemoUser):
    """
    Expect a JSON body with id and password
    Return with JWT Key
    """
    getDemoUser(userDTO=userDTO)