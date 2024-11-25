# tests/test_langchain_ollama.py

import unittest
from unittest.mock import patch, MagicMock
from langchain.llms import OllamaLLM
from src.llm_interaction import interact_with_llm

class TestLangChainOllama(unittest.TestCase):
    def setUp(self):
        # Setup tasks before each test method
        self.question = "What is the capital of France?"

    @patch('langchain.llms.OllamaLLM.generate')
    def test_ollama_llm_call(self, mock_generate):
        """
        Test that LangChain correctly calls Ollama LLM and processes the response.
        """
        # Arrange: Set up the mock response
        mock_response = MagicMock()
        mock_response.text = "The capital of France is Paris."
        mock_generate.return_value = mock_response

        # Act: Call the interact_with_llm function
        response = interact_with_llm(self.question)

        # Assert: Check that the LLM was called correctly and response is as expected
        mock_generate.assert_called_once()
        self.assertEqual(response, "The capital of France is Paris.")

    @patch('langchain.llms.OllamaLLM.generate')
    def test_ollama_llm_error_handling(self, mock_generate):
        """
        Test that the system properly handles errors from Ollama LLM.
        """
        # Arrange: Configure the mock to raise an exception
        mock_generate.side_effect = Exception("LLM service unavailable")

        # Act & Assert: Ensure that interact_with_llm raises the appropriate exception
        with self.assertRaises(Exception) as context:
            interact_with_llm(self.question)
        
        self.assertIn("Failed to get response from LLM", str(context.exception))

    def test_ollama_llm_live_service(self):
        """
        Integration test to interact with the live Ollama LLM service.
        NOTE: This test depends on external service availability and should be
        categorized separately (e.g., as an integration test).
        """
        # Arrange: Initialize the Ollama LLM
        llm = OllamaLLM(model="ollama/gpt-model")  # Replace with actual model name

        # Act: Generate a response
        response = llm.generate(self.question)

        # Assert: Check that a response is received
        self.assertIsNotNone(response.text)
        self.assertIn("capital", response.text.lower())

if __name__ == '__main__':
    unittest.main()