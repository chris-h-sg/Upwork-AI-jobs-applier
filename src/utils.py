import re
import random
# import html2text # Removed as it's no longer used after switching to API
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

COVER_LETTERS_FILE = "./data/cover_letter.md"

def extract_provider_and_model(model_string: str):
    """
    Extract the provider and model name from a given model string.

    Args:
        model_string (str): The model string in the format "provider/model".

    Returns:
        tuple: A tuple containing the provider and the model name.
    """
    return model_string.split("/", 1)

def get_llm_by_provider(model_string, temperature=0.1):
    """
    Retrieve the appropriate LLM instance based on the provider and model name.

    Args:
        model_string (str): The model string in the format "provider/model".
        temperature (float): The temperature for controlling output randomness.

    Returns:
        llm: An instance of the specified language model.

    Raises:
        ValueError: If the LLM provider is not supported.
    """
    llm_provider, model = extract_provider_and_model(model_string)
    
    # Match the provider and initialize the corresponding LLM
    if llm_provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=model, temperature=temperature)
    elif llm_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        llm = ChatAnthropic(model=model, temperature=temperature)
    elif llm_provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
    elif llm_provider == "groq":
        from langchain_groq import ChatGroq
        llm = ChatGroq(model=model, temperature=temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    
    return llm

async def ainvoke_llm(
    system_prompt,
    user_message,
    model="openai/gpt-4o-mini",  # Default to GPT-4o-mini
    response_format=None
):
    """
    Invoke a language model asynchronously with the given prompts.

    Args:
        system_prompt (str): The system-level instruction for the LLM.
        user_message (str): The user's message or query.
        model (str): The model string specifying the provider and model name.
        response_format: An optional format for structuring the output.

    Returns:
        str: The output generated by the LLM.
    """
    # Construct message inputs for the LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]  
    
    # Initialize the LLM based on the model
    llm = get_llm_by_provider(model)
    
    # Apply output parsing based on the response format
    if response_format:
        llm = llm.with_structured_output(response_format)
    else:
        llm = llm | StrOutputParser()
    
    # Execute the LLM invocation asynchronously
    output = await llm.ainvoke(messages)
    return output

# Removed get_playwright_browser_context as Playwright is no longer used.
# Removed convert_html_to_markdown as html2text is no longer a dependency
# and HTML processing is not currently done by the scraper.

def format_scraped_job_for_scoring(jobs):
    """
    Format a list of scraped jobs for scoring.

    Args:
        jobs (list): The list of scraped job data.

    Returns:
        list: A list of dictionaries representing jobs with their IDs.
    """
    return [{'id': index, **job} for index, job in enumerate(jobs)]

def convert_jobs_matched_to_string_list(jobs_matched):
    """
    Convert a list of matched jobs to a list of formatted strings.

    Args:
        jobs_matched (DataFrame): The DataFrame containing matched job data.

    Returns:
        list: A list of job descriptions as formatted strings.
    """
    jobs = []
    for job in jobs_matched:
        job_str = f"# Title: {job['title']}\n"
        job_str += f"# Experience Level: {job['experience_level']}\n"
        job_str += f"# Description:\n{job['description']}\n\n"
        job_str += f"# Proposal Requirements:\n{job['proposal_requirements']}\n"
        jobs.append(job_str)
    return jobs

def read_text_file(filename):
    """
    Read a text file and return its contents as a single string.

    Args:
        filename (str): The path to the file.

    Returns:
        str: The contents of the file.
    """
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines if line.strip()]
        return "".join(lines)
