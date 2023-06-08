# All agent related functions will be here
from webapi.toolai.config import agent
from webapi.toolai.tools import TitleMakerBasedOnQuestion

def generate_title_ai(question:str) -> str :
    return TitleMakerBasedOnQuestion().run(question)

def agent_add_ai_messages(ListMessages:list[str]=None):
    if ListMessages:
        for message in ListMessages:
            agent.memory.chat_memory.add_ai_message(message)

def agent_add_human_messages(ListMessages:list[str]=None):
    if ListMessages:
        for message in ListMessages:
            agent.memory.chat_memory.add_user_message(message)

async def agent_awaitrun(question:str):
    return await agent.arun(question)

async def agent_awaitrun_with_messages(question:str,HumanMessages:list[str],AIMessages:list[str]):
    """Runs the agent with the messages history"""
    agent_add_ai_messages(AIMessages)
    agent_add_human_messages(HumanMessages)
    return await agent.arun(question)