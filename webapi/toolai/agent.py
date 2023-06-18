# All agent related functions will be here
from webapi.toolai.tools import TitleMakerBasedOnQuestion
from langchain.agents import AgentType, initialize_agent
from webapi.toolai.tools import tool_class, tool_search_class
from webapi.toolai.config import llm,embeddings,conversational_memory
from langchain import PromptTemplate

agent = initialize_agent(
    tools= tool_class,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=conversational_memory,
    max_iterations=3,
    early_stopping_method='generate',
    verbose=True
)

# Agent Behavior Description
sys_msg = """Assistant is a large language model trained by OneBrain.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Unfortunately, Assistant is terrible at finding sources. When provided with questions asking for document source or link, no matter how simple, assistant always refers to it's trusty tools to extract view Link part which is http link that refers to the document and absolutely does NOT try to answer source finding questions by itself.

Assistant should be able to also recall the memory to be able to answer questions about their previous conversations. Assistant would be provided with the context of the previous messages.

Assistant should prioritize to not to use the tools. It should check its memory first and if no information is found valuable there, it should look for tools to search this information. When asked about an source of information, agent always uses its tools to find answer.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
"""

# new_prompt = PromptTemplate.from_template(sys_msg)

# agent.agent.llm_chain.prompt = new_prompt
# agent.tools = tool_class

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