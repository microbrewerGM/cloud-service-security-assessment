# TODO: 
# - Add better HTML template
# - Add tips/guidance/prompts within the HTML template
#   - This would look like tips to a user reading the webpage
#   - Start with the tips in the template
#       - Structure tips as a section titled `Section Guidance`
#           - Place section after the section title
#           - Have subsections for the current tips, newly added guidance (see next bullet), and LLM prompts
#   - Add guidance for each section
# - Use tips, guidance, and prompts in template to drive LLM prompt engineering
# - Use a LLM pattern to make the prompt better from the prompts, tips, guidance, and further context


def generate_llm_prompt(context, question):
    """
    Generates a prompt for the LLM using the provided context and question.

    :param context: The context extracted from the Chroma database.
    :param question: The security question to be answered.
    :return: A formatted prompt string.
    """
    prompt_template = (
        "Answer the following security question using the provided context. "
        "Your answer should be concise and based on the context.\n\n"
        "Context: {context}\n\n"
        "Security Question: {question}\n\n"
        "Answer:"
    )
    return prompt_template.format(context=context, question=question)