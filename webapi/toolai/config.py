import os
openai_api_key = os.getenv("AI_API_KEY","")
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["LANGCHAIN_TRACING"] = "true"

from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.embeddings.openai import OpenAIEmbeddings

llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        temperature=0.3,
        model_name='gpt-3.5-turbo'
)

conversational_memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True
)
conversational_memory.save_context({"input": "hi, what are you doing"}, {"output": "Hi, I am helping a customer to resolve his problems"})
conversational_memory.save_context({"input": "What issue does he face"}, {"output": "He's having problem with his internet connection"})
embeddings = OpenAIEmbeddings()


# # Import things that are needed generically
# from langchain import LLMMathChain, SerpAPIWrapper
# from langchain.agents import AgentType, initialize_agent, load_tools
# from langchain.chat_models import ChatOpenAI
# from langchain.tools import BaseTool, StructuredTool, Tool, tool
# from webapi.toolai.tools import GoogleDriveSearchTool
# from langchain.chains.conversation.memory import ConversationBufferWindowMemory
# from configs import llm, conversational_memory

# tools = [GoogleDriveSearchTool()]

# llm = ChatOpenAI(
#         openai_api_key=openai_api_key,
#         temperature=0.3,
#         model_name='gpt-3.5-turbo'
# )

# conversational_memory = ConversationBufferWindowMemory(
#         memory_key='chat_history',
#         k=5,
#         return_messages=True
# )

# # Construct the agent. We will use the default agent type here.
# # See documentation for a full list of options.
# agent = initialize_agent(
#     agent='chat-conversational-react-description',
#     tools=tools,
#     llm=llm,
#     verbose=True,
#     max_iterations=3,
#     early_stopping_method='generate',
#     memory=conversational_memory,
# )

