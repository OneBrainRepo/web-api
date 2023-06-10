from fastapi import Query, Request, APIRouter, Depends, status, WebSocket
from fastapi.responses import Response
from webapi.conversation.conversations import *
from webapi.conversation.conversation_dto import *
from webapi.auth.jwt import JWTGuard
from starlette.websockets import WebSocketDisconnect
from webapi.async_services.celery_config import redis_connection,ChannelNames, redis_retrive_message_from_channel
from webapi.async_services.http_services import single_operation_point
import ast
import json
from time import sleep

router = APIRouter()

@router.get("/protected-test")
def protected_test(current_user: dict[str,str] = Depends(JWTGuard)):
    print(f"UUID : {current_user.uuid}")
    return dict(current_user)

# Tested Ok
@router.get("/last")
def last_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_last_conversation(current_user.id)

# Tested OK
@router.get("/all")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_conversation(current_user.id)

# Tested OK
@router.get("/titles")
def all_conversation(current_user: dict[str,str] = Depends(JWTGuard)):
    return get_all_titles(current_user.id)   

# Tested OK
@router.get("/specific")
def specific_conversation(chatid : str ,current_user: dict[str,str] = Depends(JWTGuard)):
    return get_specific_coversation(userid=current_user.id,chatid=chatid)

# Tested Ok
# Used for opening a new chat window
# Creates also author if it doesnt exists
@router.post("/create")
async def create_conversation(payload:Chat_MachineAnswer_single,current_user: dict[str,str] = Depends(JWTGuard)):
    # return add_conversation(payload=payload,userid=current_user)
    return await create_new_response(payload=payload,userid=current_user)

@router.post("/append")
async def append_to_conversation(payload:ChatHistoryAppendToEnd,current_user: dict[str,str] = Depends(JWTGuard)):
    return await append_to_response(payload=payload,userid=current_user.id)

# Tested OK
@router.post("/edit_title")
def change_title(payload:ChatUpdateTitle,current_user : dict[str,str] = Depends(JWTGuard)):
    return change_conversation_title(payload=payload,userid=current_user.id)

@router.post("/edit_message")
def change_message(payload:ChatUpdateMessage,current_user : dict[str,str] = Depends(JWTGuard)):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not Implemented"
    )
    # Return is disabled since this endpoint will be avaliable after demo
    # return change_user_message(payload=ChatUpdateMessage,userid=current_user.id)

@router.get("/delete")
def delete_message(id:str,current_user : dict[str,str] = Depends(JWTGuard)):
    delete_user_message(id=id,userid=current_user.id)
    return Response(status_code=202)

# @router.get("/testmessages")
# def specific_conversation(chatid : str ,current_user: dict[str,str] = Depends(JWTGuard)):
#     objectresult = get_specific_coversation_object(userid=current_user.id,chatid=chatid)
#     userQuestionsList = objectresult['UserQuestions']
#     machineAnswersList = objectresult['MachineAnswers']
#     for i,v in enumerate(userQuestionsList):
#         print(f"User Question index : {i} Value : {v}")
#     print(type(userQuestionsList))
#     print(f"User Question : {userQuestionsList}\nMachine answers : {machineAnswersList}")
#     return True

"""
Kafka will not be implemented.
Celery will be implemented for MVP to handle tasks in the background and web notifications will be used to transfer data.

"""
# Tested OK
# This endpoint will be used append to existing conversation
# Will NOT require document ID
# To append to the last message aka current message that user is writing
# @router.post("/append_latest")
# def append_to_conversation_latest(payload:ChatHistoryAppendLatest,current_user: dict[str,str] = Depends(JWTGuard)):
#     return append_conversation_latest(payload=payload,userid=current_user.id)

# Tested OK
# This endpoint will be used to append to specific chat
# When user wants to continue on some old conversation we can use this
# @router.post("/old-append")
# def append_to_conversation(payload:ChatHistoryAppend,current_user: dict[str,str] = Depends(JWTGuard)):
#     return append_conversation(payload=payload,userid=current_user.id)

# Tested Ok
# Used for opening a new chat window
# Creates also author if it doesnt exists
# Will not be used, will be changed with /message endpoint
# @router.post("/old-create")
# def create_conversation(payload:ChatHistoryCreate,current_user: dict[str,str] = Depends(JWTGuard)):
#     return add_conversation(payload=payload,userid=current_user)
    # return create_new_response(message=payload.UserQuestions,userid=current_user.id)

# # Test endpoint for websocket
# @router.websocket("/test")
# async def websocket_test_endpoint(websocket : WebSocket):
#     await websocket.accept()
#     data = await websocket.receive()
#     try:
#         payload = ast.literal_eval(data.get('text'))
#         await websocket.send_text("Acknowledged")
        
#         rpub = redis_connection.pubsub()
#         rpub.subscribe("testchannel")

#         # Send the json over the redis
#         jsonplayload = json.dumps({
#             "message":"test"
#         })
#         redis_connection.publish("testchannel",jsonplayload)
#         """
#         If message is new call different function
#         """

#         # Get the message from redis
#         message_redis = redis_retrive_message_from_channel(rpub)
#         # Serialize JSON back
#         json_response = json.loads(message_redis)
#         await websocket.send_json({
#             "data":json_response,
#             "recived": payload
#         })
#     except WebSocketDisconnect:
#             print("Client disconnected")
#     except Exception as e:
#         print(f"Exception at /message websocket\n{e}")
#         await websocket.close(code=1008,reason=f"An error occured during the processing of the data. Error : {e}")
#         return

# # Token needs to be parsed as parameter
# @router.websocket("/message")
# async def websocket_message(websocket : WebSocket):
#     await websocket.accept()
#     while True:
#         try:
#             # Keep connection open
#             data = await websocket.receive()
#             payload = ast.literal_eval(data.get('text'))
#             parsed_payload = MessageWebSocketPayload.parse_obj(payload)
#             # Extract jwt token
#             found_user = JWTGuard(token=parsed_payload.token)
#             # Send first Acknowledgement
#             await websocket.send_text("Acknowledged")
#             # Define Channel Name
#             channel_name = f"{ChannelNames.single_channel_response}_{found_user.uuid}"
#             print(f"Communication channel name : {channel_name}")
#             # # Subscribe to redis
#             pubsub = redis_connection.pubsub() # DISABLE THIS FOR NOW
#             pubsub.subscribe(channel_name) # DISABLE THIS
#             # Parse this channel name to the celery
#             single_operation_point.delay(payload={ # DISABLE FROM HERE
#                 "question":parsed_payload.UserMessage,
#                 "user_uuid": found_user.uuid
#             },channel_name=channel_name,user_data=found_user)
#             # Check the message response in a loop
#             while True:

#                 fine_tuned_answer = redis_retrive_message_from_channel(pubsub)# THIS DISABLE AS WELL
#                 json_response = json.loads(fine_tuned_answer)
#                 # Check the answer later on whether it has valuable answer or gibberish
#                 # Send message back to user after that
#                 await websocket.send_json({ # NOTE : IF ABOVE CODE IS DISABLED THIS WILL RUN INDEFINETLY
#                     "message":"acknowledged",
#                     "data":json_response
#                 })
#         except WebSocketDisconnect:
#             print("Client disconnected")
#             break
#         except Exception as e:
#             print(f"Exception at /message websocket\n{e}")
#             await websocket.close(code=1008,reason=f"An error occured during the processing of the data. Error : {e}")
#             return

# @router.get("/testdel")
# def testdel(params:str):
#     print(f"passed aprams : {params}")
#     return Response(status_code=201)