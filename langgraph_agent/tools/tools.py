import os, time, random, logging
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv
import snowflake
import snowflake.connector
from langchain_core.tools import tool
import os
from typing import List, Dict
import threading
import faiss
# from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
import os, re, threading
import json
import numpy as np 
from pydantic import BaseModel
import pickle
from tavily import AsyncTavilyClient
from dotenv import load_dotenv

@tool
async def web_search(query: str) -> str:
    """
    Perform a web search using the Tavily API.
    Args:
        query (str): The search query.
    Returns:
        str: The results from the Tavily search.
    """
    load_dotenv(override=True)

    tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    response = await tavily_client.search(query)

    return str(response)
