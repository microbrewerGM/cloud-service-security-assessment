import json
from jinja2 import Environment, FileSystemLoader
import os
import fitz  # PyMuPDF
from chromadb.config import Settings
import chromadb
import logging
import time  # Ensure to import time if not already imported

# Initialize logging for utils.py
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get template directory and name from environment variables
template_dir = os.getenv('TEMPLATE_DIR', 'data/templates')  # Provide a default if needed
template_name = os.getenv('TEMPLATE_NAME', 'report_template.html')  # Provide a default
template_path = os.path.join(template_dir, template_name)
logging.info(f"Attempting to load template from: {template_path}")

# Set up Jinja2 environment with the template directory
env = Environment(loader=FileSystemLoader(template_dir))

class PDFChromaLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PDFChromaLoader, cls).__new__(cls)
            try:
                cls._instance.pdf_text = cls._load_pdf_text()
                cls._instance.collection = cls._create_chroma_collection(cls._instance.pdf_text)
                logging.info("PDFChromaLoader initialized successfully.")
            except FileNotFoundError as e:
                logging.error(e)
                raise e
            except Exception as e:
                logging.error(f"Error initializing PDFChromaLoader: {e}")
                raise e
        return cls._instance

    @classmethod
    def _load_pdf_text(cls):
        pdf_file = os.getenv('PDF_FILE_NAME')
        if not pdf_file:
            raise ValueError("PDF_FILE_NAME environment variable not set.")
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")
        logging.info(f"Loading PDF file from: {pdf_file}")
        return cls._extract_text_from_pdf(pdf_file)

    @staticmethod
    def _extract_text_from_pdf(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            logging.info(f"Extracted text from PDF: {pdf_path}")
            return text
        except Exception as e:
            logging.error(f"Failed to extract text from PDF: {e}")
            raise e

    @classmethod
    def _create_chroma_collection(cls, pdf_text):
        try:
            client = chromadb.Client(Settings(anonymized_telemetry=False))  # Adjusted initialization
            collection = client.create_collection("all-my-documents")
            collection.add(
                documents=[pdf_text],
                metadatas=[{"source": "pdf"}],
                ids=["pdf1"]
            )
            logging.info("ChromaDB collection created successfully.")
            return collection
        except Exception as e:
            logging.error(f"Failed to create ChromaDB collection: {e}")
            raise e

    @classmethod
    def get_pdf_text(cls):
        return cls._instance.pdf_text

    @classmethod
    def get_chroma_collection(cls):
        return cls._instance.collection

def load_security_questions(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            questions = data.get('questions', [])
            logging.info(f"Loaded {len(questions)} security questions from {file_path}")
            return questions
    except FileNotFoundError:
        logging.error(f"Security questions file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format in security questions file: {e}")
        raise

def render_html(template_name, questions):
    logging.info(f"Loading template: {template_name}")
    try:
        template = env.get_template(template_name)
        logging.info(f"Template '{template_name}' loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading template: {e}")
        return ""  # Return an empty string or handle as needed
    return template.render(questions=questions)