from pydantic import BaseModel, Field

class CalculatePower(BaseModel):
    first_var :int = Field(description="First integer value which will be base in the operation")
    second_var :int = Field(description="Second integer value which will be power in the operation")

class UserDocumentSearch(BaseModel):
    question :str = Field(description="User question itself")
    keywords :str = Field(description="Keywords extracted from User question itself. Will be used in searching. Seperate each words by comma(,) . If users asks about summary or link do not include verbal keywords like 'summary' or 'link' in the search. Keywords should be descriptive enough to be used in searching literal keyword in the document. For example if users asks you 'Can you summarize me X Company agreement with its shareholders', keywords should be X Company,agreement,shareholder . Use non plural as much as possible to avoid mismatching.")
    connection_id :str = Field(description="A string input that used in searching through google drive. This variable allows tool to search through user documents")

class NotionPageSearch(BaseModel):
    question: str = Field(description="User question itself")