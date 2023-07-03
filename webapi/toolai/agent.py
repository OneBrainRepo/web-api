# All agent related functions will be here
from webapi.toolai.tools import TitleMakerBasedOnQuestion
from langchain.agents import AgentType, initialize_agent, StructuredChatAgent, AgentExecutor
from webapi.toolai.tools import tool_class, tool_search_class, UserDocumentSearchAsynchronously, DuckDuckGoTool
from webapi.toolai.config import llm,embeddings,conversational_memory
from langchain import PromptTemplate, LLMChain
from langchain.chains.summarize import load_summarize_chain
import langchain

langchain.debug = True

# Agent Behavior Description
sys_msg = """Assistant is a large language model trained by OneBrain.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Unfortunately, Assistant is terrible at finding sources. When provided with questions asking for document source or link, no matter how simple, assistant always refers to it's trusty tools to extract view Link part which is http link that refers to the document and absolutely does NOT try to answer source finding questions by itself.

Assistant should be able to also recall the memory to be able to answer questions about their previous conversations. Assistant would be provided with the context of the previous messages.

Assistant should prioritize to not to use the tools. It should check its memory first and if no information is found valuable there, it should look for tools to search this information. When asked about an source of information, agent always uses its tools to find answer.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
ou have access to the following tools:
"""

suffix = """Begin!"

Question: {input}
{agent_scratchpad}"""

prompt = StructuredChatAgent.create_prompt(
    tool_class,
    prefix=sys_msg,
    suffix=suffix,
    input_variables=["input", "agent_scratchpad"],
)

llm_chain = LLMChain(llm=llm, prompt=prompt)
agent_struct = StructuredChatAgent(llm_chain=llm_chain, tools=tool_class, verbose=True)

agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent_struct, tools=tool_class, verbose=True
)

summary_chain = load_summarize_chain(llm, chain_type="map_reduce")


agent = initialize_agent(
    tools= tool_class,
    llm=llm,
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    # memory=conversational_memory,
    max_iterations=2,
    early_stopping_method='generate',
    verbose=True
)

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

def duckduckgo_search_agent(Question:str):
    print("Calling Agent DuckDuckGo")
    docs = DuckDuckGoTool(Question)
    return summary_chain.run(docs)

async def tool_debug(input):
    inputdict = {
        "question": "What is Ethan's role in Agorapp?",
        "keywords": "Ethan, role, Agorapp",
        "connection_id": "googledrive__arslasercan@gmail.com"
    }
    debuggedtool = UserDocumentSearchAsynchronously()
    result = await debuggedtool._arun(connection_id=inputdict.get('connection_id'),keywords=inputdict.get('keywords'),question=inputdict.get('question'))
    print(result)
    return result