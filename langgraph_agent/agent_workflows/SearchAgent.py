from __future__ import annotations
from langgraph_agent.agent_workflows.LangGraphAgent import LangGraphAgentSystem
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from dotenv import load_dotenv
import os
# from langfuse import Langfuse
# from langfuse.callback import CallbackHandler
import pandas as pd
from typing import Optional, Dict, Any
from gen_utils.parsing_utils import retrieve_secret
import pandas as pd 
from typing import Union
import os
import pandas as pd
import numpy as np
from typing import Dict
from langgraph.checkpoint.memory import MemorySaver
from typing import List
# from langgraph_agent.structured_output.structured_outputs import OutputResponse, AgentState
from langgraph_agent.tools.tools import web_search
from phoenix.otel import register
# from tools.tools import web_search
from tavily import AsyncTavilyClient

@tool
async def web_search(query: List[str]) -> str:
    """
    Perform a web search using the Tavily API.
    Args:
        query List(str): The search queries.
    Returns:
        str: The results from the Tavily search.
    """
    load_dotenv(override=True)

    tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    responses = []
    
    for q in query:
        response = await tavily_client.search(q)
        responses.append(response)

    return str(responses)




class SearchAgent(LangGraphAgentSystem):
    """
    This class implements a LangGraph agent workflow for product mapping using Azure OpenAI and Langfuse.
    It initializes the model, creates tools, and manages the workflow between the mapper agent and scraper agent.
    The workflow is designed to handle product name analysis and SKU matching with the PMA database.
    """

    def create_tools(lg):
        """ 
        Creates the tools for the LangGraph agent.
        This method initializes the tools used by the agent, including:
        - `query_pma`: A tool for querying the PMA database.
        - `scrape_product_size_uom`: A tool for scraping product size and unit of measure from the web.
        The tools are then assigned to the agent's search_tools and scraper_tools attributes.    
        """
        
        lg.search_tools = [web_search]
        lg.tools = [web_search]

    def initialize_model(self):
        """
        Initializes the Azure OpenAI model with Langfuse monitoring and tools binding.

        This method performs the following tasks:
        1. Loads environment variables using `dotenv`.
        2. Initializes the Langfuse client and callback handler for monitoring and logging.
        3. Configures the Azure OpenAI model with the API key, endpoint, and deployment name.
        4. Binds tools to the model and sets up structured output handling.

        Attributes set:
        - `self.langfuse`: An instance of the Langfuse client for monitoring.
        - `self.langfuse_handler`: A Langfuse callback handler for interaction logging.
        - `self.model_with_tools`: The Azure OpenAI model with tools bound to it.
        - `self.model_with_structured_output`: The Azure OpenAI model with structured output handling.

        Raises:
            KeyError: If any required environment variable is not found.
            Exception: If there is an error during model initialization.

        Returns:
            None
        """
        # Load environment variables
        load_dotenv()
        retrieve_secret(secret_name='des-o3', project_id='cd-ds-384118')

        # # configure the Phoenix tracer
        tracer_provider = register(
            project_name="search-agent", # Default is 'default'
            endpoint="https://devpoc.compassdigital.io:443/phoenix-arize/v1/traces",
            auto_instrument=True # Auto-instrument your app based on installed dependencies
        )

        # Load Azure OpenAI API credentials
        AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
        AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")

        # Validate required credentials
        if not (AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT_NAME):
            raise KeyError("Missing Azure OpenAI API credentials in environment variables.")

        openai_api_version_4o = "2024-08-01-preview"
        openai_api_version_o3 = "2024-12-01-preview"
        # Initialize the Azure OpenAI model
        model = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            openai_api_version=openai_api_version_o3,
            openai_api_key=AZURE_OPENAI_API_KEY,
            deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME,
            # temperature=0.0,  # For deterministic output
        )

        # Bind tools to the model
        self.model_with_tools = model.bind_tools(self.tools)

        # Set up structured output
        model_with_structured_output = model.with_structured_output(self.input_dict['structured_output_class'])

        # Assign models to instance attributes
        self.search_model_with_tools = model.bind_tools(self.search_tools)
        self.model_with_structured_output = model_with_structured_output


    async def respond(self, state: MessagesState) -> Dict[str, Union[str, HumanMessage]]:
        """
        Responds to the user by processing the last tool message and invoking the model
        with structured output to maintain consistent formatting.

        This method checks if the third-to-last message in the state is a `ToolMessage`.
        If so, it converts the tool's output into a `HumanMessage` and invokes the model 
        to generate a structured response. If no tool message is found, it exits gracefully.

        Parameters:
            state (MessagesState): The current state of the conversation, including a list of messages.

        Returns:
            Dict[str, Union[str, HumanMessage]]: A dictionary containing the final response:
                - "final_response": A structured response from the model if a tool was invoked,
                or an exit message if no tool was called.
        """
        response = await self.model_with_structured_output.ainvoke(
            state['messages']
        )
        # Return the final structured response
        return {"final_response": response}

        
    def search_should_continue(self, state: MessagesState) -> str:
        """
        Drive the workflow based on the last message:
        - If no tool is mentioned or called, respond to the user.
        - If the model text includes 'semantic_search', route back into search_tools.
        - After a tool has executed, inspect which tool:
            * query_pma → go back to search_agent to process results
            * scrape_product_size_uom → return to search_agent to combine scraped size
        """
        messages = state["messages"]
        last_msg = str(messages[-1])
        print("search Agent: ", last_msg)
        # 2) No tool run yet, inspect the model’s text to see intent
        text = last_msg
        if "web_search" in text:
            # model is asking to query PMA → run search_tools
            return "search_tools"
        if "agent_respond" in text:
            # model is asking to scrape size → hand off to scraper_agent
            return "agent_respond"
        return "agent_respond"
    

    async def call_model(self, state: MessagesState, agent_prompt:str="agent_prompt", model:Any="") -> Dict[str, List[SystemMessage]]:
        """
        Calls the model with the provided state and appends the system message.

        This method appends a system message containing the agent's prompt to the existing message state,
        invokes the model to generate a response, and returns the updated state.

        Parameters:
            state (MessagesState): The current state of the conversation, including a list of messages.

        Returns:
            Dict[str, List[SystemMessage]]: A dictionary containing the updated messages, 
            including the model's response.

        Attributes:
            self.input_dict (Dict): A dictionary containing configurations, including the agent's prompt.
            self.model_with_tools: The model instance with tools bound, used for generating responses.

        Example:
            state = {
                "messages": [HumanMessage(content="What's the weather in SF?")]
            }
            result = call_model(state)
            print(result["messages"])
        """
        
        # Append the agent's system message to the conversation
        if SystemMessage(content=self.input_dict[agent_prompt]) not in state['messages']:
            state['messages'].append(SystemMessage(
                content=self.input_dict[agent_prompt]
            ))

        if model == "":
            # Call the model with the updated message state (async)
            response = await self.model_with_tools.ainvoke(state["messages"])
        else:
            # Call the model with the updated message state (async)
            response = await model.ainvoke(state["messages"])
        
        # Return the updated messages as a list
        return {"messages": [response]}

    
    async def create_workflow(self) -> Any:
        """
        Creates and executes a workflow for managing the conversation flow between an agent, tool interactions, 
        and user responses.

        This method defines a `StateGraph` to handle the conversation workflow, including conditional transitions
        based on whether the agent should continue processing or respond to the user. It compiles the workflow 
        and invokes it with the input message, returning the final result.

        Workflow Overview:
            - Nodes:
                - "search_agent": Handles model invocation using `call_model`.
                - "agent_respond": Handles user responses using `respond`.
                - "search_tools": Handles tool interactions using a `ToolNode`.
            - Entry Point: "search_agent"
            - Transitions:
                - From "search_agent":
                    - If `should_continue` returns "continue", transitions to "search_tools".
                    - If `should_continue` returns "agent_respond", transitions to "agent_respond".
                - From "search_tools", transitions back to "search_agent".
                - From "agent_respond", ends the workflow (`END`).

        Parameters:
            None

        Returns:
            Any: The output of the workflow after invoking the graph, typically the final response.
        """
        # Define a new graph
        workflow = StateGraph(self.input_dict['agent_state'])

        # Define the three nodes in the workflow
        async def search_agent_node(state):
            return await self.call_model(state, 'search_agent_prompt', self.search_model_with_tools)
        
        async def agent_respond_node(state):
            return await self.respond(state)

        workflow.add_node("search_agent", search_agent_node)
        workflow.add_node("agent_respond", agent_respond_node)
        workflow.add_node("search_tools", ToolNode(self.search_tools))

        # Set the entry point to "search_agent"
        workflow.set_entry_point("search_agent")

        # Add conditional edges from "search_agent" based on `should_continue`
        workflow.add_conditional_edges(
            "search_agent",
            self.search_should_continue,
            {
                "search_tools": "search_tools",  # Transition to "search_tools" if `should_continue` returns "search_tools"
                "agent_respond": "agent_respond"  # Transition to "agent_respond" if `should_continue` returns "agent_respond"
            },
        )

        # Define other edges
        workflow.add_edge("search_tools", "search_agent")  # Cycle back to "search_agent" from "search_tools"
        workflow.add_edge("agent_respond", END)   # End the workflow from "agent_respond"

        memory = MemorySaver()
        # Compile the workflow into a graph
        graph = workflow.compile()

        # Invoke the graph with the initial input and callback handler (async)
        answer = await graph.ainvoke(
            input={"messages": [("human", self.input_dict['input_prompt'])]}
            # config={"callbacks": [self.langfuse_handler]}
        )

        # Save graph
        self.graph = graph

        return answer

    async def run(self) -> Any:
        """
        Executes the main workflow for the agent, including tool creation, model initialization, 
        and workflow execution.
        """
        # Step 1: Create tools
        self.create_tools()

        # Step 2: Initialize the model
        self.initialize_model()

        # Step 3: Create and execute the workflow (now async)
        answer = await self.create_workflow()

        # Store the final response
        self.answer = answer

        # Return the final response
        return answer
        
