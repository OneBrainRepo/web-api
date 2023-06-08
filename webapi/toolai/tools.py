from langchain.tools import tool, BaseTool
from pydantic import BaseModel, Field
from typing import List, Any
from langchain.docstore.document import Document
from webapi.toolai.google_drive import google_drive_search
from webapi.toolai.llm_functions import qa_over_document
from langchain.llms import OpenAI

llm = OpenAI()


"""
IMPORTANT  UPDATE

TOOL NEEDS TO BE DEFINED AS ONE SINCE GOOGLE DRIVE ONE RETURNS REALLY LONG STRING AND THIS CANNOT BE PARSED BACK TO LLM
THEREFORE WE NEED TO HANDLE EVERYTHING UNDER GOOGLE DRIVE TOOL
"""

# WE MIGHT NEED TO WRITE IT AS CLASS TO MAKE IT HAPPEN

class GoogleDriveSearchTool(BaseTool):
    name = "Google Drive Search Tool"
    description = "Searches the Google drive documents over the given question, find answers and returns it back"

    async def _arun(self, userquestion: str) -> Any:
        print("GoogleDriveTool._arun() is being called")
        keywords_predicted = llm.predict(f"I am looking for generating keywords to optimize my search. I need you to generate a string response with all the keys you think are required for this search. The string response needs to be comma seperated. The String response should look like this 'keyword1,keyword2' where values are string arrays. You should return me only String response nothing else, no comment nothing. If user asking for view link, source or anything similar to that you should omit those as a keyword. So please generate the response for the following question : {userquestion}")
        title = llm.predict(f"Also please provide a title which summarizes user question. I want you to return just a String output, nothing more. Here is the user question : {userquestion}")
        keywords = keywords_predicted.split(',')
        print(f"Keywords : {keywords}\nUser Question : {userquestion}\nKeywords Predicted : {keywords_predicted}\nTitle : {title}")
        results = await google_drive_search(keywords=keywords) 
        answer =  qa_over_document(document_list=results,question=userquestion)
        # foundDocs = results
        #
        return answer

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        print("GoogleDriveTool._run() is being called")
        raise NotImplemented("This tool can only run asynchronously!")

class TitleMakerBasedOnQuestion(BaseTool):
    name = "Title Creator"
    description= "Creates a title/headline based on the given question"
    def _run(self, userquestion: str) -> Any:
        print("TitleMakerBasedOnQuestion._run() is being called")
        return llm.predict(f"Also please provide a title which summarizes user question. I want you to return just a String output, nothing more. Here is the user question : {userquestion}")
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplemented("This tool only can be run as synchronously")

# class DocumentQATool(BaseTool):
#     name= "Document Question Answers Tool"
#     description = "Gets the list of documents and user question and returns the answer of user question by using document. It is document QA tool"

#     def _run(self, user_question: str) -> Any:
#         print("DocumentQATool._run() is being called")
#         result =  qa_over_document(document_list=foundDocs,question=user_question)
#         return result

#     def _arun(self, *args: Any, **kwargs: Any) -> Any:
#         print("DocumentQATool._arun() is being called")
#         raise NotImplemented("This tool only can be run as synchronously")

# async def run_google_drive_tool_async(google_drive_tool: GoogleDriveTool, keywords: str) -> Any:
#     return await google_drive_tool._arun(keywords=keywords)
