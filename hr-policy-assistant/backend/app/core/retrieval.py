import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from flashrank import Ranker, RerankRequest

from app.core.prompts import CHAT_PROMPT
from app.core.guardrails import SemanticGuardrail

load_dotenv()

# --- CONFIGURATION & PATHS ---
USE_CLOUD = os.getenv("USE_CLOUD", "True") == "True"
LOCAL_OLLAMA_URL = "http://192.168.1.21:11434" # Update with your local Ollama URL if different use localhost or IP address 
CLOUD_OLLAMA_URL = "https://ollama.com"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(CORE_DIR))
VECTOR_DB_DIR = os.path.join(BACKEND_DIR, "vector_db")

# Initialize Vector DB, Guardrails, and FlashRank for high-accuracy reranking
embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5", base_url=LOCAL_OLLAMA_URL)
vector_db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
guardrail = SemanticGuardrail(embeddings)
ranker = Ranker()

# Toggle between local Llama and cloud-based high-performance models
if USE_CLOUD:
    llm = ChatOllama(
        model="gpt-oss:20b-cloud", 
        base_url=CLOUD_OLLAMA_URL,
        client_kwargs={"headers": {"Authorization": f"Bearer {OLLAMA_API_KEY}"}},
        temperature=0
    )
else:
    llm = ChatOllama(model="llama3.2:latest", base_url=LOCAL_OLLAMA_URL, temperature=0)

# --- QUERY REWRITER ---
# Converts follow-ups (e.g., "What about medical?") into full questions using history
rewrite_system_prompt = "Formulate a standalone question from the chat history and latest user query. Do not answer it."
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", rewrite_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])
rewriter_chain = rewrite_prompt | llm | StrOutputParser()

# In-memory storage for user chat sessions
sessions_db = {}

def get_session_history(session_id: str):
    return sessions_db.setdefault(session_id, [])

# --- RETRIEVAL ENGINE ---
def process_context(input_data):
    original_query = input_data["question"]
    history = input_data.get("chat_history", [])
    
    # Block non-HR topics immediately
    if guardrail.is_out_of_scope(original_query):
        return "GUARDRAIL_TRIGGERED"

    # Contextualize the query if it's a follow-up question
    search_query = original_query
    if history:
        try:
            search_query = rewriter_chain.invoke({"question": original_query, "chat_history": history}).strip().strip('"')
        except Exception as e:
            print(f"Rewriting failed: {e}")

    # Fetch 12 candidates using Maximum Marginal Relevance (MMR) for diversity
    initial_docs = vector_db.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": 12, "fetch_k": 25}
    ).invoke(search_query)
    
    # Remove identical text blocks to save tokens
    seen = set()
    unique_passages = []
    for i, doc in enumerate(initial_docs):
        text = doc.page_content.strip()
        if text.lower() not in seen:
            seen.add(text.lower())
            unique_passages.append({"id": i, "text": text, "metadata": doc.metadata})

    if not unique_passages: return ""

    # Use FlashRank to pick the top 3 most relevant passages from the candidates
    rerank_request = RerankRequest(query=search_query, passages=unique_passages)
    results = ranker.rerank(rerank_request)
    
    # Format the findings with clear source and page citations
    formatted_passages = []
    for r in results[:3]:
        meta = r.get('metadata', {})
        block = f"[[ SOURCE: {meta.get('source', 'Unknown')} | PAGE: {meta.get('page', 'N/A')} ]]\n{r['text']}"
        formatted_passages.append(block)
    
    return "\n\n---\n\n".join(formatted_passages)

# --- CHAIN ORCHESTRATION ---
def route_output(input_data):
    # Handle guardrail blocks and "no data" scenarios gracefully
    if input_data["context"] == "GUARDRAIL_TRIGGERED":
        return "I am an HR Assistant and can only answer policy-related questions."
    if not input_data["context"]:
        return "I couldn't find information on that in the HR handbook."
    return core_llm_chain.invoke(input_data)

core_llm_chain = CHAT_PROMPT | llm | StrOutputParser()

rag_chain = (
    RunnablePassthrough.assign(context=process_context)
    | RunnableLambda(route_output)
)

def query_documents(user_question: str, session_id: str = "default"):
    # Main entry point: Manages history, invokes the chain, and returns the answer
    history = get_session_history(session_id)
    try:
        answer = rag_chain.invoke({"question": user_question, "chat_history": history})
        
        # Keep only the last 10 messages to prevent context overflow
        history.append(HumanMessage(content=user_question))
        history.append(AIMessage(content=answer))
        sessions_db[session_id] = history[-10:] 
        return answer
    except Exception as e:
        return f"System Error: {str(e)}"