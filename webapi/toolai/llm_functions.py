# Maybe split the character later on rather then now
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from typing import List

# General Settings
# llm = OpenAI(model="curie")
llm = OpenAI()
embeddings = OpenAIEmbeddings()

# Not necessary for now
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# ethan_document = text_splitter.split_text(ethan_clime_doc)
# for docs in ethan_document:
#   ethan_documents.append(Document(page_content=docs))

"""
Error happens down below at the Querying results part.
"""
class LongTextSplitter:
    def __init__(self, chunk_size=600, chunk_overlap=0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text):
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

def split_text_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

chunk_size = 600



def qa_over_document_without_source(document_list : List[Document],question:str):
    print(f"Calling Document QA")
    docsearch = Chroma.from_documents(document_list, embeddings)
    print("Calling RetrievalQA")
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
    print("Querying Result")
    result = qa.run(question)
    print(f"Result : {len(result)}\n{result}")
    return result

def qa_over_document(document_list : List[Document],question:str):
    print(f"Calling Document QA")
    if not document_list:
        # Fail to retrive information
        return "I am sorry but I am not able to get any information according to my search right now."
    
    docsearch = Chroma.from_documents(document_list, embeddings,metadatas=[{"source": f"{i}"} for i in range(len(document_list))])
    print("Calling RetrievalQA")
    qa = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever())
    print("Querying Result")
    # result = qa.run(question)
    result = qa({"question": f"{question}"}, return_only_outputs=True)
    print(f"Result : {len(result)}\n{result}")
    return result