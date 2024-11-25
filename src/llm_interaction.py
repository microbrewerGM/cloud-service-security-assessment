import os
from langchain_community.chains.llm_requests import LLMRequestsChain
from langchain_core.prompts import PromptTemplate
from src.llm_prompts import generate_llm_prompt
from src.utils import PDFChromaLoader
from langchain_ollama import OllamaLLM # Return error message for debugging

def enhance_prompt_with_context(question):
    collection = PDFChromaLoader.get_chroma_collection()
    results = collection.query(query_texts=[question], n_results=1)
    context = results['documents'][0] if results['documents'] else "No relevant context found."
    return generate_llm_prompt(context, question)

def interact_with_llm(question):
    ollama_api_url = os.getenv('OLLAMA_API_URL')
    ollama_model = os.getenv('OLLAMA_MODEL')
    enhanced_prompt = enhance_prompt_with_context(question)
    enhanced_prompt = enhanced_prompt.replace('{', '{{').replace('}', '}}')  # Escape curly braces
    ollama_llm = OllamaLLM(model=ollama_model,api_url=ollama_api_url)
    return ollama_llm.invoke(enhanced_prompt)
