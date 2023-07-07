from langchain.tools import StructuredTool, BaseTool
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain, ConversationalRetrievalChain
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.docstore.document import Document
from langchain.tools import DuckDuckGoSearchRun
from typing import Optional, Type, List, Any
import re

from webapi.toolai.google_args_schema import CalculatePower, UserDocumentSearch, NotionPageSearch
from webapi.toolai.google_drive import google_drive_search_synchronous, google_drive_search
from webapi.toolai.notion_tool import notion_get_content_document
from webapi.toolai.config import llm,embeddings

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
# Define the class



class GetPowerValue(BaseTool):
    name="GetPowerValue"
    description="With given two input, it will raise first input to power of second input. Both inputs needs to be integer"
    args_schema : Type[CalculatePower] | None = CalculatePower
    def _run(self, first_var:str , second_var:str) -> int:
        if((type(first_var) != int) or (type(second_var) != int)):
            raise ValueError("Both values needs to be integer. Please provide integer values")
        return first_var**second_var

    async def _arun(self, query: str,  engine: str = "google", gl: str = "us", hl: str = "en", run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

class UserDocumentSearchOnDrive(BaseTool):
    name="GoogleDriveDocumentSearch"
    description="Searches through User's google drive with provided connection_id and question. It uses connection id variable to access to the google drive and searches keywords that are extracted from the user question"
    args_schema : Type[UserDocumentSearch] | None = UserDocumentSearch

    def _run(self, question: str, keywords:str, connection_id:str, run_manager : Optional[CallbackManagerForToolRun] = None) -> str:
        print(f"Started Execution of UserDocumentSearchOnDrive on _run()")
        try:
            keywords = re.sub(r"\s+", "", keywords)
            keywords = keywords.split(",")
        except Exception as e:
            print("[LOGERR] Exception occured on Keyword generation for google drive")
            print(f"Error code : {e}")
            return "Mention user that there was a problem with the searching and we couldnt generate keywords out of user question. Ask user to define his question in more descriptive manner"
        
        document_list = google_drive_search_synchronous(keywords=keywords,connection_id=connection_id)
        if not document_list:
            return "No documents has been found."
        docsearch = Chroma.from_documents(document_list, embeddings,metadatas=[{"source": f"{i}"} for i in range(len(document_list))])
        print("Calling RetrievalQA")
        qa = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
        print("Querying Result")
        # result = qa.run(question)
        result = qa({"question": f"{question}"}, return_only_outputs=True)
        print(f"Result : {len(result)}\n{result}")
        return result

    async def _arun(self, query: str,  engine: str = "google", gl: str = "us", hl: str = "en", run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

class UserDocumentSearchAsynchronously(BaseTool):
    name="GoogleDriveDocumentSearchAsynchronously"
    description="Searches through User's google drive asynchronously with provided connection_id and question. It uses connection id variable to access to the google drive and searches keywords that are extracted from the user question. Use this one for google drive document search more often since it can handle requests asynchronously, it is performance optimized. Call this function via _arun method. It is asynchronous"
    args_schema: Type[UserDocumentSearch] | None = UserDocumentSearch

    async def _arun(self, question: str, keywords:str, connection_id:str, run_manager : Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        # Keywords might not be list of strings currently, therefore split them by comma
        print(f"Started Execution of UserDocumentSearchAsynchronously on _arun()")
        try:
            print(f"Keywords currently : {keywords}")
            # keywords = re.sub(r"\s+", "", keywords)
            keywords = keywords.split(" ")
            print(f"Keywords after split : {keywords}")
        except Exception as e:
            print("[LOGERR] Exception occured on Keyword generation for google drive")
            print(f"Error code : {e}")
            return "Mention user that there was a problem with the searching and we couldnt generate keywords out of user question. User should provide more descriptive question to search through"
        document_list = await google_drive_search(keywords=keywords,connection_id=connection_id)
        if not document_list:
            # No document found error
            return "No documents has been found. Please return user that you were not able to find anything. Do not write any information from yourself. Simply tell user that no information has been found with the given question and ask him to check his spelling if there is any typo or mistake. ."
        print("Searching through documents")
        if type(document_list) == str:
            # Document list has returned an error
            return "Respond to user as : Sorry there was an error occured, please ask again"
        from langchain.vectorstores import Chroma
        docsearch = Chroma.from_documents(document_list, embeddings,metadatas=[{"source": f"{i}"} for i in range(len(document_list))])
        print("Calling RetrievalQA")
        # qa = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
        print(f"Calling Alternative QA with Conversational chain")
        from langchain.memory import ConversationBufferMemory
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        qa_alternative = ConversationalRetrievalChain.from_llm(llm=llm,retriever=docsearch.as_retriever(),memory=memory,verbose=True)
        # qa = ConversationalRetrievalChain.from_llm(llm=llm,retriever=docsearch.as_retriever(),eturn_source_documents=True) Will try this one in the future
        print("Querying Result")
        # result = qa.run(question)
        result_alternative = qa_alternative({"question":question})
        # result = qa({"question": f"{question}"}, return_only_outputs=True)
        # print(f"Result : {len(result)}\n{result}")
        # delete chroma
        del docsearch
        del Chroma

        return result_alternative
    def _run(self, question: str, keywords:str, connection_id:str) -> str:
        raise NotImplementedError("Google Drive Document Search Asynchronously does not support sync, it only works async")

class TitleMakerBasedOnQuestion(BaseTool):
    name = "TitleCreator"
    description= "Creates a title based on the given question. It should return the topic summary as a title that user would be able to understand what is the title about"
    def _run(self, userquestion: str) -> Any:
        print("TitleMakerBasedOnQuestion._run() is being called")
        return llm.predict(f"Also please provide a title which summarizes user question. I want you to return just a String output, nothing more. Do not indicate title seperately. Just return whatever you think suitable as a text. Here is the user question : {userquestion}")
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplemented("This tool only can be run as synchronously")

def DuckDuckGoTool(Question:str) -> List[Document] :
    print("Calling DuckDuckGoTool")
    search = DuckDuckGoSearchRun()
    result = search.run(Question)
    docs = [Document(page_content=result)]
    return docs

class SearchOnNotionTool(BaseTool):
    name="NotionSearch"
    description= "Searches on notion on every page where user has access to it. Finds the all pages and does semantic search in order to return user question"
    args_schema: Type[NotionPageSearch] | None = NotionPageSearch
    def _run(self,question:str,run_manager : Optional[CallbackManagerForToolRun] = None) -> Any:
        print("SearchOnNotionTool._run() is being called")
        document_list = notion_get_content_document()
        docsearch = Chroma.from_documents(document_list, embeddings)
        print("Calling RetrievalQA")
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
        # qa = ConversationalRetrievalChain.from_llm(llm=llm,retriever=docsearch.as_retriever(),eturn_source_documents=True) Will try this one in the future
        print("Querying Result")
        # result = qa.run(question)
        result = qa.run(question)
        print(f"Result : {len(result)}\n{result}")
        return result
    async def _arun(self,question:str,run_manager : Optional[AsyncCallbackManagerForToolRun] = None) -> Any:
        print("SearchOnNotionTool._arun() is being called")
        document_list = await notion_get_content_document()
        docsearch = Chroma.from_documents(document_list, embeddings)
        print("Calling RetrievalQA")
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
        # qa = ConversationalRetrievalChain.from_llm(llm=llm,retriever=docsearch.as_retriever(),eturn_source_documents=True) Will try this one in the future
        print("Querying Result")
        # result = qa.run(question)
        result = qa.run(question)
        print(f"Result : {len(result)}\n{result}")
        return result

tool_class = [UserDocumentSearchAsynchronously(),GetPowerValue()]
tool_search_class = [UserDocumentSearchAsynchronously()]