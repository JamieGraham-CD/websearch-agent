import os
from typing import List, Dict, Any, TypedDict, Annotated, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from tavily import AsyncTavilyClient
from pydantic import BaseModel, Field
from gen_utils.parsing_utils import retrieve_secret
from langgraph_agent.agent_workflows.SearchAgent import SearchAgent
from langgraph.graph import MessagesState
from langgraph.graph import add_messages

# -- Load keys from env --
# TODO: Implementation of the graph


# Execute search workflow
async def execute_search_workflow(query:str) -> Tuple[Dict[str,Any], SearchAgent]:
    """ 
    This function executes a search agent that retrieves information from the web with sources.
    It uses a structured output format to ensure clarity and correctness in the generated code.
    Args:
        query (str): The query to be searched.
    Returns:
        Tuple[Dict[str, Any], searchAgentWorkflow]: A tuple containing the generated code and the agent workflow instance.
    """
    # Retrieve the secrets for the Google Cloud project
    retrieve_secret(project_id='cd-ds-384118', secret_name='generalized-parser-des')

    # Load the system and user prompts from files
    with open('./langgraph_agent/prompts/search_system_prompt.txt', 'r') as f:
        search_system_prompt = f.read()
    with open('./langgraph_agent/prompts/structured_output_agent_prompt.txt', 'r') as f:
        structured_output_agent_prompt = f.read()
        structured_output_agent_prompt = ""

    # # Extract the attribute from the structured output schema
    # attribute = dict(structured_output.schema()).get("title")
    class ExampleStructuredOutput(BaseModel):
        response: str = Field(description="The response from the search agent")
        sources: List[str] = Field(description="The url sources from the search agent")

    class AgentState(MessagesState):
        # Final structured response from the agent
        messages: Annotated[list,add_messages]
        final_response: ExampleStructuredOutput


    # Define the input dictionary for the MapperAgentWorkflow
    input_dict = {
        "input_prompt": f'''{query}''',
        "search_agent_prompt":search_system_prompt,
        "agent_state":AgentState,
        "structured_output_class":ExampleStructuredOutput,
        "structured_output_agent_prompt": structured_output_agent_prompt
    }

    # Initialize the MapperAgentWorkflow with the input dictionary
    lg = SearchAgent(input_dict)


    # Run the workflow (now async)
    answer = await lg.run()


    return answer.get('final_response'), lg


async def run_graph(question: str) -> Dict:
    # TODO: Implementation of the graph execution

    answer, graph_object = await execute_search_workflow(question)

    result = {"final_answer": answer.model_dump()}
    
    return result