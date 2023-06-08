import httpx
from webapi.async_services.celery_config import celery_app, redis_connection, ChannelNames
from webapi.async_services.async_dto import AsyncUserQuestionCelery
from webapi.db.models import Users, Demo
import ast
import os

"""
Write a basic tasks that gets the payload and returns user acknowledgement
It is for testing Celery and asynchrnous processes
Later on we need to create celery service for OpenAI sedimentation, Tool calling and answer fine tuning
After everything has been done it should return user back with an answer
"""
# OPENAPIKEY = os.environ("OPEN_API_KEY","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")
# # HOSTS information
# ONLIZER_BASE_HOST = "https://onebrain.onlizer.com/"
# ONLIZER_SEARCH_GDRIVE = "api/v1/googledrive/search"
# GPT_MODEL_HOST = "https://api.openai.com/v1/chat/completions"
# GPT_MODEL_TURBO = "gpt-3.5-turbo"
# # Will be used pre-processing of the user input
# INFORMATIVE_TEXT = "I am looking for generating keywords to optimize my search. I need you to generate a JSON response with all the keys you think are required for this search. JSON body should look like this {'keywords':values} where values are string arrays. You should also add possible service names that those keywords must be searched at. If it is just a conversation, you can add service name as `conversation`. Currently avaliable Service names are google_drive, conversation. You should also define recommended actions for the services. Action can be read,create,update,delete .  In that case, the JSON response should look like {'google_drive' : {'action': values, 'keyword':,values}} . You should return me only JSON response nothing else, no comment nothing. So please generate the response for the following question: "
# FINE_TUNE_TEXT = lambda question,answer : f"Here is the question : {question}\nHere is the information i gathered about that question : {answer} \nPlease write me an fine tuned answer for this question with provided information. Do not write any explaination. I just need your output prompt as answer as it is coming from a friend to another friend, human likely. Do not write any here is your found answer or anything similar. Directly friendly answer"

"""
Check if parsing assistant context(in this case machine answer to the fine tuned text) makes sense to include in the messages.
Also check for parsing whole data like keyword extracted user question asked and machine answers previously aka user and assistant message history with provided outputs
"""

# Endpoint Calling Function

async def invoke_endpoint_async(url:str,body:dict={},headers:dict={},req_type : str="GET"):
    """
    Get URL, Request Type, Headers, Body
    URL - url = str URL address of the endpoint
    Request type - req_type =  "POST" | "GET" HTTP Method
    Body - body = dict | None Only required when post request is invoked
    Headers - headers = dict | None Headers that will be parsed in the request

    Call with await keywords
    r = await invoke_endpoint_async(**params)
    """
    async with httpx.AsyncClient() as client:
        if req_type == "POST":
            return await client.post(url=url,json=body,headers=headers)
        elif req_type == "GET":
            return await client.get(url=url,params=body,headers=headers)
        else:
            return None


# Single Celery task for right now
@celery_app.task
async def single_operation_point(payload:AsyncUserQuestionCelery,channel_name:str,user_data:Users):
    return False
    # question = payload.UserMessage
    # user_uuid = payload.useruui
    
    # # NOT TESTED ON AWAIT BUT FUNCTION ITSELF WORKS
    # # NEEDS CONNECTION ID
    # # THIS CONNECTION ID NEEDS TO BE EXTRACTED FROM CONNECTION TABLE WHICH HAS RELATION WITH THE USER TABLE 
    # # NEED TO EXTRACT USER CONNECTION ID AND PARSE IT
    # """
    # CALL NEW PART
    # ALSO MODIFY KEYWORD ANALYSES TO GET ONLY KEYWORD NOT JSON OR GET JSON WITH LIST OF SERVICES
    # """
    # # found_words = await gdrive_search(keyword_analyzes_json,connection_id="<NEED CONNECTION ID>")
    # found_words = "empty"
    # # FINE TUNE THE ANSWER ACCORDINGLY
    # # DO token counting
    
    # # DO token counting
    # fine_tune_answer = await invoke_endpoint_async(url=GPT_MODEL_HOST,body={
    #     "model": GPT_MODEL_TURBO,
    #     "messages": [{"role": "user", "content": FINE_TUNE_TEXT(question=question,answer=found_words)}],
    #     "max_tokens": 800
    # },headers=headers,req_type="POST")
    # # Publish the message after it has been responded
    # fine_tune_response = fine_tune_answer.json().get('choices')[0].get('message').get('content') # Fine tuned answer
    # # Write it to database again this time with the machine answer
    # # DB WRITING
    # # Add another DB entry called summary which will collect summary of the conversation, will take it from the langchain
    # # Check pine cone article for that
    # # Call either create or append
    # """
    # SHOULD CALL PREVIOUS MESSAGES AS WELL TO PROVIDE LONG TERM MEMORY AS WELL
    # https://www.pinecone.io/learn/langchain-conversational-memory/
    # """
    # if payload.messageType == "new":
    #     print("CREATE NEW MESSAGE")
    # elif payload.messageType == "append":
    #     print("APPEND TO EXISTING MESSAGE")
    # else :
    #     print("A PROBLEM OCCURED")
    # # Publish it on specific uuid channel RESPOND WITH JSON OBJECT RATHER THEN JUST A FINE TUNED ANSWER
    # print("RESPONSE NEEDS TO BE STRING BINARY INT OR FLOAT, DICT CANNOT BE PARSED DIRECTLY")
    # print("CURRENTLY RETURNED DATA IS STRING")
    # redis_connection.publish(channel_name,fine_tune_response)


# async def keyword_analyzer(usermessage:str):
#     """
#     OPTIONS ARE SEARCH, VIEW, AND CONVERSATION
#     DO NOT SHARE THE FULL TEXT AT ALL AND IF USER ASKS FOR FULL DETAIL ONLY PROVIDE VIEW LINK 
#     usermessage - User's question
#     """
#     headers = {
#     'Content-Type': 'application/json',
#     'Authorization': f"Bearer {OPENAPIKEY}"
#     }
#     keyword_analyzes = await invoke_endpoint_async(url=GPT_MODEL_HOST,body={
#         "model": GPT_MODEL_TURBO,
#         "messages": [{"role": "user", "content": INFORMATIVE_TEXT + usermessage}],
#         "max_tokens": 600
#     },headers=headers,req_type="POST")
#     # 
#     # EXTRACT THE CONTENT
#     # CONVERT IT TO JSON/DICT 
#     # 
#     keyword_analyzes_answer = keyword_analyzes.json().get('choices')[0].get('message').get('content') # Keywords
#     keyword_analyzes_json = ast.literal_eval(keyword_analyzes_answer)
#     """
#     DEFINE WHETHER IT IS A CONVERSATION OR TOOL REQUIRED APPLICATION THEN CALL THE TOOL TO EXECUTE THE TASK
#     CURRENTLY ONLY TOOL SUPPORTED WILL BE GOOGLE_DRIVE_SEARCH
    """

# @celery_app.task
# async def get_keyword_analysis(payload,useruuid):
#     """
#     This function is here to get an JSON response from NLP to parse data into specific keywords
#     """

#     async with httpx.AsyncClient() as client:
#         response = await client.post("https://api.openai.com/v1/davinci-codex/completions", json={
#             "prompt": INFORMATIVE_TEXT + payload['UserMessage'],
#             "max_tokens": 60
#         })
#         summary = response.json()['choices'][0]['text']
        
#         # Call necessary services
#         # result = necessaryServicesCall(summary)
        
#         # Send result back to user
#         # add_conversation(payload=payload, machine_answer=result)

# @celery_app.task
# def example_endpoint(payload):
#     # Call OpenAI endpoint to get JSON response for text analysis
#     # This is an example calling of redis_connection
#     redis_connection.publish(ChannelNames.fine_tuning_process,"fine_tuned_operation")
#     # Example consuming
#     pubsub = redis_connection.pubsub()
#     pubsub.subscribe(ChannelNames.fine_tuning_process)