import json
import unittest
import os
from unittest import mock
from dotenv import load_dotenv

load_dotenv()

class TestSecurityQuestionsJson(unittest.TestCase):
    def setUp(self):
        """
        Set up the environment for the tests.
        """
        # Load the SECURITY_QUESTIONS_FILE environment variable
        
        # Retrieve the SECURITY_QUESTIONS_FILE environment variable
        self.security_questions_path = os.environ.get('SECURITY_QUESTIONS_FILE')

        if not self.security_questions_path:
            self.fail("Environment variable 'SECURITY_QUESTIONS_FILE' is not set.")

    @mock.patch.dict(os.environ, {'SECURITY_QUESTIONS_FILE': 'data/security_questions.json'})
    def test_load_security_questions(self):
        """
        Test loading security questions from the JSON file specified by the environment variable.
        """
        # Attempt to open and load the JSON file
        try:
            with open(self.security_questions_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.fail(f"File '{self.security_questions_path}' not found.")
        except json.JSONDecodeError:
            self.fail(f"File '{self.security_questions_path}' is not a valid JSON.")

        # Check that the data structure is as expected
        self.assertIn('questions', data)
        self.assertIsInstance(data['questions'], list)
        self.assertGreater(len(data['questions']), 0, "No questions found in the JSON file.")

        # Optionally, check the structure of the first question
        first_question = data['questions'][0]
        self.assertIn('id', first_question)
        self.assertIn('text', first_question)
        self.assertIn('guidance', first_question)

if __name__ == '__main__':
    unittest.main()