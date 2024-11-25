import logging
import os
import json
import time  # Ensure time is imported
from dotenv import load_dotenv
from src.llm_interaction import interact_with_llm
from src.utils import render_html, PDFChromaLoader, load_security_questions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

def validate_environment_variables():
    required_vars = [
        'SECURITY_QUESTIONS_FILE',
        'TEMPLATE_DIR',
        'TEMPLATE_NAME',
        'OUTPUT_DIR',
        'OLLAMA_API_URL',
        'OLLAMA_MODEL',
        'PDF_FILE_NAME'
    ]
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    if missing_vars:
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

def validate_dependencies():
    # Validate environment variables
    if not validate_environment_variables():
        return False

    # Validate template file
    template_dir = os.getenv('TEMPLATE_DIR', 'data/templates')
    template_name = os.getenv('TEMPLATE_NAME', 'report_template.html')
    template_path = os.path.join(template_dir, template_name)
    if not os.path.exists(template_path):
        logging.error(f"Template file not found: {template_path}")
        return False

    # Validate security questions file
    questions_file = os.getenv('SECURITY_QUESTIONS_FILE')
    if not os.path.exists(questions_file):
        logging.error(f"Security questions file not found: {questions_file}")
        return False

    # Validate PDF file
    pdf_file = os.getenv('PDF_FILE_NAME')
    if not os.path.exists(pdf_file):
        logging.error(f"PDF file not found: {pdf_file}")
        return False

    return True

def generate_html_report():
    # Load the security questions file from the environment variable
    questions_file = os.getenv('SECURITY_QUESTIONS_FILE')

    # Load the questions
    try:
        questions = load_security_questions(questions_file)
    except FileNotFoundError:
        logging.error("Security questions file not found.")
        return
    except json.JSONDecodeError:
        logging.error("Security questions file is not a valid JSON.")
        return

    # Iterate through each question and get the LLM response
    for question in questions:
        # Debugging: Check the type of question
        logging.info(f"Processing question: {question} (type: {type(question)})")

        # Ensure question is a dictionary and has 'text'
        if isinstance(question, dict) and 'text' in question:
            logging.info(f"Processing question text: {question['text']}")
            try:
                llm_response = interact_with_llm(question['text'])
                question['llm_response'] = llm_response  # Add the LLM response to the question dict
                logging.info(f"LLM response added for question ID {question.get('id')}")
            except Exception as e:
                logging.error(f"Failed to get LLM response for question ID {question.get('id')}: {e}")
                question['llm_response'] = "Error retrieving response."
        else:
            logging.error(f"Invalid question format: {question}")
            question['llm_response'] = "Invalid question format."

    # Load the HTML template with updated questions
    template_name = os.getenv('TEMPLATE_NAME', 'report_template.html')
    try:
        html_content = render_html(template_name, questions)
        logging.info("HTML content rendered successfully.")
    except Exception as e:
        logging.error(f"Error rendering HTML content: {e}")
        return

    # Create a timestamp for the output file
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS

    # Define the output directory and ensure it exists
    output_dir = os.getenv('OUTPUT_DIR', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    # Define the output file path with timestamp
    output_file_path = os.path.join(output_dir, f'report_{timestamp}.html')  # Change to .pdf if needed

    try:
        with open(output_file_path, 'w') as f:
            f.write(html_content)
        logging.info(f"Report generated successfully at {output_file_path}")
    except Exception as e:
        logging.error(f"Failed to write HTML report: {e}")

def main():
    load_dotenv()  # Load environment variables from .env file

    # Validate all dependencies before proceeding
    if not validate_dependencies():
        logging.error("Dependency validation failed. Exiting.")
        return

    # Initialize PDF and ChromaDB loading
    try:
        PDFChromaLoader()  # Initialize the singleton instance
    except FileNotFoundError as e:
        logging.error(e)
        return
    except Exception as e:
        logging.error(f"Error initializing PDFChromaLoader: {e}")
        return

    # Continue with the rest of your application logic
    generate_html_report()

if __name__ == "__main__":
    main()