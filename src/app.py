import logging
import os
import json
import time  # Ensure time is imported
from dotenv import load_dotenv
from src.llm_interaction import interact_with_llm
from src.utils import render_html, PDFChromaLoader, load_security_questions
from bs4 import BeautifulSoup

load_dotenv()  # Load environment variables from .env file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("app.log"),
        logging.FileHandler(os.getenv('LOG_PATH')),
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
        logging.info(f"Processing question ID {question.get('id')}: {question.get('text')}")
        if isinstance(question, dict) and 'text' in question:
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

    # Extract 'Request' text from the template
    template_dir = os.getenv('TEMPLATE_DIR', 'data/templates')
    template_name = os.getenv('TEMPLATE_NAME', 'report_template.html')
    template_path = os.path.join(template_dir, template_name)
    request_text = extract_request_from_template(template_path)

    if request_text:
        # Format the request as '<p><b>Request:</b> text</p>'
        formatted_request = f"<p><b>Request:</b> {request_text}</p>"
        logging.info(f"Formatted Request for LLM: {formatted_request}")

        # Send the formatted request to LLM
        try:
            llm_risk_overview = interact_with_llm(formatted_request)
            risk_overview = {
                "llm_response": llm_risk_overview
            }
            logging.info("LLM response for risk overview added successfully.")
        except Exception as e:
            logging.error(f"Failed to get LLM response for risk overview: {e}")
            risk_overview = {
                "llm_response": "Error retrieving response."
            }
    else:
        logging.error("No request text extracted. Skipping risk overview LLM query.")
        risk_overview = {
            "llm_response": "No request provided."
        }

    # Load the HTML template with updated questions and risk overview
    try:
        html_content = render_html(template_name, questions, risk_overview=risk_overview)
        logging.info("HTML content rendered successfully.")
    except Exception as e:
        logging.error(f"Error rendering HTML content: {e}")
        return

    # Create a timestamp for the output file
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS

    # Define the output directory and ensure it exists
    output_dir = os.getenv('OUTPUT_DIR')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    # Define the output file path with timestamp
    output_file_path = os.path.join(output_dir, f'report_{timestamp}.html')  # Change to .pdf if needed

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"Report generated successfully at {output_file_path}")
    except Exception as e:
        logging.error(f"Failed to write HTML report: {e}")

def extract_request_from_template(template_path):
    """
    Extracts the text within the <h4>Request</h4><p>text</p> elements from the HTML template.

    :param template_path: Path to the HTML template file.
    :return: Extracted request text or None if not found.
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Locate the Security Review Details section
        section = soup.find('section', {'id': 'security-review-details'})
        if not section:
            logging.error("Section with id 'security-review-details' not found in template.")
            return None

        # Find the <h4>Request</h4> tag
        request_header = section.find('h4', string='Request')
        if not request_header:
            logging.error("<h4>Request</h4> tag not found in 'security-review-details' section.")
            return None

        # The next sibling <p> tag contains the request text
        request_paragraph = request_header.find_next_sibling('p')
        if not request_paragraph:
            logging.error("Paragraph containing the request text not found after <h4>Request</h4>.")
            return None

        request_text = request_paragraph.get_text(strip=True)
        if not request_text:
            logging.error("Request text is empty.")
            return None

        logging.info(f"Extracted request text: {request_text}")
        return request_text

    except Exception as e:
        logging.error(f"Error extracting request from template: {e}")
        return None
    
def main():
    # load_dotenv()  # Load environment variables from .env file

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