import httpx
import json
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
import requests

class LongTextSplitter:
    def __init__(self, chunk_size=600, chunk_overlap=0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

def split_text_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

chunk_size = 600

async def invoke_endpoint_async(url:str,body:dict={},headers:dict={},req_type : str="GET",timeout:int = 60):
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
        try:
            if req_type == "POST":
                return await client.post(url=url,json=body,headers=headers,timeout=timeout)
            elif req_type == "GET":
                return await client.get(url=url,params=body,headers=headers,timeout=timeout)
            else:
                return None
        except Exception as e:
            raise RuntimeError(e)

def parse_remove_escape_characters(jsonstr:str):
    return jsonstr.replace("\r","").replace("\n","").replace("\"","")

"""
ONLIZER API WILL HAVE BASE TEMPLATE FOR NOW
NO AND OPERATOR OR OTHER THINGS
ONLY ONE PARSER
"""
def google_drive_search_synchronous(keywords : List[str],connection_id:str):
    """
    RETURNS Document or False
    Document - Strings that wrapped around Document class
    Boolean - False for API call fails 

    WORKWAY
    FIRSTLY CHECKS FOR SUMMARY OF THE WORDS
    IF NOT FOUND GOES FOR PARAGRAHP APPENDING
    IF IT IS NOT THEN GOES FOR FULL TEXT
    """
    
    url = "https://onebrain.onlizer.com/api/v1/googledrive/search"

    payload = json.dumps({
    "keywords": keywords,
    "connectionId": connection_id,
    "options": {
        "searchOperator": "and",
        "returnFullText": False,
        "tokensSearchOperator": "or",
        "tokens": [
        "paragraphs",
        "summary"
        ]
    }
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ZDE2YThmNGU3ODhhODkwMTdkMjQ5ZDA1ZmMwM2I2ZGY6OWFkNThmODE5OWViNmFjNmU4NWRkNjI2NTIyZTJhMGE='
    }
    try:
        search_results = requests.request("POST", url, headers=headers, data=payload)
    except Exception as e:
        print(f"Error Occured during Google Drive Search\nError : {e}")
        return "Error Occured during Google Drive Search"
    if search_results.status_code != 200:
        print(f"[LOGERR] Connection Error | Status Code : {search_results.status_code}")
        if search_results.status_code == 400:
            print("[LOGERR] Request parameter has unmatched keys in the body")
            return "Tool is missing parameters to complete this search. If this issue is persistent please report it"
        if search_results.status_code == 500:
            print("[LOGERR] Onlizer API is down")
            return "Search API is currently unavaliable"
    # Process data
    docs_found = search_results.json().get('files')
    del search_results
    wholesummary = google_drive_documentizer(docs_found=docs_found)
    if not wholesummary:
        return False
    return wholesummary

async def google_drive_search(keywords : List[str],connection_id:str):
    """
    RETURNS Document or False
    Document - Strings that wrapped around Document class
    Boolean - False for API call fails 

    WORKWAY
    FIRSTLY CHECKS FOR SUMMARY OF THE WORDS
    IF NOT FOUND GOES FOR PARAGRAHP APPENDING
    IF IT IS NOT THEN GOES FOR FULL TEXT
    """
    
    url = "https://onebrain.onlizer.com/api/v1/googledrive/search"

    payload = {  
    "keywords":keywords,  
    "connectionId":connection_id,  
    "options":{  
        "searchOperator":"and",  
        "returnFullText":True,  
        "tokensSearchOperator": "or",  
        "tokens": ["paragraphs", "summary"]  
    }  
    }
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ZDE2YThmNGU3ODhhODkwMTdkMjQ5ZDA1ZmMwM2I2ZGY6OWFkNThmODE5OWViNmFjNmU4NWRkNjI2NTIyZTJhMGE='
    }
    try:
        print(f"Current Payload : {payload}")
        search_results = await invoke_endpoint_async(url=url,body=payload,headers=headers,req_type="POST")
    except Exception as e:
        print(f"Error Occured during Google Drive Search\nError : {e}")
        return "Error Occured during Google Drive Search"
    if search_results.status_code != 200:
        print(f"[LOGERR] Connection Error | Status Code : {search_results.status_code}")
        if search_results.status_code == 400:
            print("[LOGERR] Request parameter has unmatched keys in the body")
            return "Tool is missing parameters to complete this search. If this issue is persistent please report it"
        if search_results.status_code == 500:
            print("[LOGERR] Onlizer API is down")
            return "Search API is currently unavaliable"
    # Process data
    docs_found = search_results.json().get('files')
    del search_results
    wholesummary = google_drive_documentizer(docs_found=docs_found)
    if not wholesummary:
        return False
    return wholesummary

def google_drive_documentizer(docs_found:list,option:int = 1):
    # Do not forget to wrap it with the viewLink part in the metadata,
    texts = [
        Document(
            page_content=chunk + ' View link to document: ' + str(doc.get('viewLink', '')), 
            word_count=len(chunk.split()),
            metadata={"source":str(doc.get('viewLink', ''))}
        )
        for doc in docs_found if doc
        for chunk in split_text_into_chunks(
            ' '.join([
                entry['text']
                for paragraph in (doc.get('paragraphs') or []) if 'entries' in paragraph and paragraph['entries']
                for entry in (paragraph['entries'] or []) if 'text' in entry and entry['text']
            ]),
            chunk_size
        )
    ]
    summaries = [
        Document(
            page_content=chunk + ' View link to document: ' + str(doc.get('viewLink', '')), 
            word_count=len(chunk.split()),
            metadata={"source":str(doc.get('viewLink', ''))}
        )
        for doc in docs_found if doc
        for chunk in split_text_into_chunks(
            (doc.get('summary') or '') + ' View link to document: ' + str(doc.get('viewLink', '')),
            chunk_size
        )
    ]
    if not option:
        return texts
    else: 
        if option == 1:
            return summaries
        else:
            return texts if len(summaries)<1 else summaries




def google_drive_summarizer(docs_found:list,options:int):
    """
    Gets a list of json then parse it back the summary according to 
    [1]summary - keyword that should be included if not
    [2]paragraphs - sum of the paragrahps
    [3]all - Will not be called since paragraphs are enough
    Default : 
    Most optimal will be returned 
    It returns false if no valuable information is found
    """
    # summaries = ' '.join([str(doc.get('summary', '')) for doc in docs_found])
    # Summaries with the link
    summaries = ' '.join([
    str(doc.get('summary', '')) + ' View link to document: ' + str(doc.get('viewLink', '')) 
    for doc in docs_found
    ])
    # Include viewLink at the end of paragrahps
    texts = ' '.join([
    ' '.join([
        entry['text']
        for paragraph in (doc.get('paragraphs') or []) if 'entries' in paragraph and paragraph['entries']
        for entry in (paragraph['entries'] or []) if 'text' in entry and entry['text']
    ]) + ' View link to document: ' + str(doc.get('viewLink', ''))
    for doc in docs_found if doc
    ])
    # texts = ' '.join([
    # entry['text'] 
    # for doc in docs_found if doc and 'paragraphs' in doc and doc['paragraphs'] is not None
    # for paragraph in doc['paragraphs'] if paragraph and 'entries' in paragraph and paragraph['entries'] is not None
    # for entry in paragraph['entries'] if entry and 'text' in entry and entry['text'] is not None
    # ])
    summaries = parse_remove_escape_characters(summaries)
    texts = parse_remove_escape_characters(texts)
    if options == 3 :
        return summaries,texts
    elif options == 2 :
        return texts
    elif options == 1 :
        return summaries
    else :
        if (len(summaries)<50) and (len(texts) < 50):
            return False
        else :
            if len(summaries)<200:
                return texts
            else :
                return summaries