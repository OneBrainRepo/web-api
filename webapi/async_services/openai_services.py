import httpx
from webapi.async_services.celery_config import celery_app, redis_connection, ChannelNames
from webapi.async_services.async_dto import AsyncUserQuestionCelery
import ast

"""
Write a basic tasks that gets the payload and returns user acknowledgement
It is for testing Celery and asynchrnous processes
Later on we need to create celery service for OpenAI sedimentation, Tool calling and answer fine tuning
After everything has been done it should return user back with an answer
"""
# Will be used pre-processing of the user input
INFORMATIVE_TEXT = "I am looking for generating keywords to optimize my search. I need you to generate a JSON response with all the keys you think are required for this search. JSON body should look like this {'keywords':values} where values are string arrays. You can also use logical operators like AND OR to make the search more optimized. In that case, the JSON response should look like {'AND' : {'keywords': values}, 'OR' : {'keywords' : values}} . You should return me only JSON response nothing else, no comment nothing. So please generate the response for the following question: "
FINE_TUNE_TEXT = lambda question,answer : f"Here is the question : {question}\nHere is the information i gathered about that question : {answer} \nPlease write me an fine tuned answer for this question with provided information. Do not write any explaination. I just need your output prompt as answer as it is coming from a friend to another friend, human likely. Do not write any here is your found answer or anything similar. Directly friendly answer"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer <TOKENGPT>'
}

"""
Check if parsing assistant context(in this case machine answer to the fine tuned text) makes sense to include in the messages.
Also check for parsing whole data like keyword extracted user question asked and machine answers previously aka user and assistant message history with provided outputs
"""

# Single Celery task for right now
@celery_app.task
async def single_operation_point(payload:AsyncUserQuestionCelery,channel_name:str):
    question = payload.UserMessage
    user_uuid = payload.useruui
    async with httpx.AsyncClient() as client:
        # Keyword analyzes first
        keyword_analyzes = await client.post("https://api.openai.com/v1/chat/completions", json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": INFORMATIVE_TEXT + question}],
            "max_tokens": 600
        },headers=headers)
        keyword_analyzes_answer = keyword_analyzes.json().get('choices')[0].get('message').get('content') # Keywords
        # Split OR and AND keywords seperately
        keyword_analyzes_json = ast.literal_eval(keyword_analyzes_answer)
        OR_KEYWORDS = keyword_analyzes_json.get('OR').get('keywords')
        AND_KEYWORDS = keyword_analyzes_json.get('AND').get('keywords')
        # Write it in the database
        #### CALL NECESSARY GOOGLE ENDPOINT ###

        #### ANALYZE THE OUTPUT 
        hypotethical_answer = "Johhny is a man, so far up to our knowledge."
        #### FINE TUNE THE ANSWER
        fine_tune_answer = await client.post("https://api.openai.com/v1/chat/completions", json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": FINE_TUNE_TEXT(question=question,answer=hypotethical_answer)}],
            "max_tokens": 800
        },headers=headers)
        # Publish the message after it has been responded
        fine_tune_response = fine_tune_answer.json().get('choices')[0].get('message').get('content') # Fine tuned answer
        # Write it to database again this time with the machine answer
        # DB WRITING
        # Call either create or append
        if payload.messageType == "new":
            print("CREATE NEW MESSAGE")
        elif payload.messageType == "append":
            print("APPEND TO EXISTING MESSAGE")
        else :
            print("A PROBLEM OCCURED")
        # Publish it on specific uuid channel RESPOND WITH JSON OBJECT RATHER THEN JUST A FINE TUNED ANSWER
        redis_connection.publish(channel_name,fine_tune_response)


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