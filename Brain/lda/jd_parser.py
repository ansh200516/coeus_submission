import logging
from typing import Dict, List

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_cerebras import ChatCerebras
from pydantic import BaseModel, Field

# A new, dedicated prompt for parsing job descriptions.
JD_PARSER_PROMPT = """You are an expert technical recruiter and HR analyst. Below is the full text of a job description. Your task is to carefully read the text and extract the key details.

Focus on the following fields:
- responsibilities: A list of the primary duties and tasks for the role.
- requirements: A list of the essential skills, qualifications, and experience needed.
- stipend: Any mention of salary, stipend, or compensation.
- location: The location of the job (e.g., "Remote", "San Francisco, CA").

Return your response as a single, clean JSON object with keys for "responsibilities", "requirements", "stipend", and "location". The value for each key should be a list of strings.

JOB DESCRIPTION TEXT:
---
{jd_text}
---
"""

# Pydantic model for structured JD output
class ParsedJD(BaseModel):
    responsibilities: List[str] = Field(description="List of job responsibilities")
    requirements: List[str] = Field(description="List of skills and qualifications")
    stipend: List[str] = Field(description="Stipend or compensation details")
    location: List[str] = Field(description="Job location")


async def parse_job_description_with_llm(jd_text: str) -> Dict:
    """Uses an LLM to parse a job description into a structured format."""
    logger = logging.getLogger(__name__)
    logger.info("Parsing job description with LLM...")

    try:
        # Using a smaller, faster model for this focused task is efficient.
        parser_llm = ChatCerebras(model="llama-4-maverick-17b-128e-instruct", temperature=0.1)
        
        parser = JsonOutputParser(pydantic_object=ParsedJD)
        
        prompt = ChatPromptTemplate.from_template(
            template=JD_PARSER_PROMPT,
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | parser_llm | parser
        
        return await chain.ainvoke({"jd_text": jd_text})
    except Exception as e:
        logger.error(f"Failed to parse job description with LLM: {e}", exc_info=True)
        # Return an empty structure on failure
        return {
            "responsibilities": [],
            "requirements": [],
            "stipend": [],
            "location": [],
        }
