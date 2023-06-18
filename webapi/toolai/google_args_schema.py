from pydantic import BaseModel, Field

class CalculatePower(BaseModel):
    first_var :int = Field(description="First integer value which will be base in the operation")
    second_var :int = Field(description="Second integer value which will be power in the operation")

class UserDocumentSearch(BaseModel):
    question :str = Field(description="User question itself")
    keywords :str = Field(description="Keywords extracted from User question itself. Will be used in searching. Seperate each words by comma(,)")
    connection_id :str = Field(description="A string input that used in searching through google drive. This variable allows tool to search through user documents")