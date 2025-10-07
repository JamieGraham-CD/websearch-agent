# Technical Coding Interview

For the technical coding interview, you will build a micro-service with **FastAPI**, **LLM**, **LangChain**, **LangGraph**, and **Tavily API**.  
Your micro-service should take a user question as input, ask search engine for information, and return a final answer + a list of sources used as reference in the end.

---

## Requirements

### Setup
1. Pull the code from the provided repository.  
2. Create a Python virtual environment locally, and install dependencies from the `requirements.txt` file.
3. Run the microservice locally.  
You can then call the API with the curl command:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
        "question": "How to cook eggs in Chinese way"
      }'
```

### Implementation
1. Design and implement the API + LangGraph AI workflow, so it will take a user question as input, and return an answer + a list of sources (search engine results) that the answer is based on.
2. Feel free to use LLM or Google for coding. This interview is open-book.
3. Feel free to ask any questions to the interviewers, or discuss your thoughts. We would encourage you to think loud.

* The API keys (burner keys from free accounts) are provided in the boilerplate code.
* Tavily search API: https://docs.tavily.com/documentation/api-reference/endpoint/search
