from fastapi import Query, Request, APIRouter
from webapi.demo_service.demo_service import return_empty_200

router = APIRouter()
#Define Demo related routes here
@router.get("/test")
def getDemoTest()-> dict:
    return return_empty_200()