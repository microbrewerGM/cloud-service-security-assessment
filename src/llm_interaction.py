import os
import logging
from src.llm_prompts import generate_llm_prompt
from src.utils import PDFChromaLoader
from langchain_ollama import OllamaLLM

def enhance_prompt_with_context(question):
    collection = PDFChromaLoader.get_chroma_collection()
    results = collection.query(query_texts=[question], n_results=1)
    context = results['documents'][0] if results['documents'] else "No relevant context found."
    return generate_llm_prompt(context, question)

def interact_with_llm(question):
    try:
        ollama_api_url = os.getenv('OLLAMA_API_URL')
        ollama_model = os.getenv('OLLAMA_MODEL')
        
        if not ollama_api_url or not ollama_model:
            logging.error("OLLAMA_API_URL or OLLAMA_MODEL environment variable not set.")
            raise Exception("Failed to get response from LLM")
        
        enhanced_prompt = enhance_prompt_with_context(question)
        ollama_llm = OllamaLLM(model=ollama_model, api_url=ollama_api_url)
        response = ollama_llm.invoke(enhanced_prompt)
        
        if not response:
            logging.error("Received empty response from LLM.")
            raise Exception("Failed to get response from LLM")
        
        return response
    except TimeoutError as te:
        logging.error(f"Timeout during LLM invocation: {te}")
        raise Exception("Failed to get response from LLM") from te
    except Exception as e:
        logging.error(f"Error during LLM interaction: {e}")
        raise Exception("Failed to get response from LLM") from e