import logging
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from audio import InterviewTTS
from knowledge_db import KnowledgeDatabase
from prompts import (
    FINAL_REVIEW_PROMPT,
    GRILLING_INTERVIEWER_PROMPT,
    LIE_DETECTION_SYSTEM_PROMPT,
    NUDGE_GENERATION_SYSTEM_PROMPT,
    generate_simple_nudge_text,
)
from utils import sanitize_llm_json_output, strip_markdown

load_dotenv()


# ========== LIE DETECTION AGENT (from lie_agent.py) ========== 
class ClaimAnalysis(BaseModel):
    """Data model for a single analyzed claim."""

    claim: str = Field(description="Exact text from transcript")
    lie: bool = Field(description="Whether this claim is likely a lie")
    confidence: float = Field(description="Confidence score 0-1", ge=0, le=1)
    reasoning: str = Field(description="Explanation of analysis")
    category: str = Field(
        description="Category: experience|education|skills|personal|other"
    )


class InterviewAnalysisOutput(BaseModel):
    """Data model for the final output of the lie detection agent."""

    claims_analyzed: List[ClaimAnalysis] = Field(
        description="List of analyzed claims", default=[]
    )
    extracted_claims: List[Dict[str, Any]] = Field(
        description="New factual claims to add to interview context", default=[]
    )
    overall_assessment: str = Field(
        description="Brief summary of analysis", default=""
    )
    flags_raised: int = Field(
        description="Number of potential lies detected", default=0
    )


class LieDetectionAgent:
    """Agent responsible for analyzing transcripts and detecting potential lies."""

    def __init__(self, knowledge_db: KnowledgeDatabase, llm_client: ChatCerebras):
        self.knowledge_db = knowledge_db
        self.llm = llm_client
        self.output_parser = PydanticOutputParser(
            pydantic_object=InterviewAnalysisOutput
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", LIE_DETECTION_SYSTEM_PROMPT),
                ("human", "TRANSCRIPT TO ANALYZE:\n{transcript}"),
            ]
        )
        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(sanitize_llm_json_output)
            | self.output_parser
        )

    async def analyze_transcript_batch(
        self,
        transcript: str,
    ) -> InterviewAnalysisOutput:
        """Analyzes a batch of transcript text against the knowledge base."""
        all_verified = [
            claim
            for claim in self.knowledge_db.entries
            if claim.source in ("linkedin", "resume")
        ]
        full_context = "\n".join([f"✓ {claim.claim}" for claim in all_verified])
        result = await self.chain.ainvoke(
            {
                "transcript": transcript,
                "verified_facts": full_context,
                "format_instructions": self.output_parser.get_format_instructions(),
            }
        )
        for claim_analysis in result.claims_analyzed:
            self.knowledge_db.add_interview_claim(
                claim=claim_analysis.claim,
                lie=claim_analysis.lie,
                confidence=claim_analysis.confidence,
                category=claim_analysis.category,
            )
        for extracted_claim in result.extracted_claims:
            if extracted_claim.get("confidence", 0) > 0.7:
                self.knowledge_db.add_interview_claim(
                    claim=extracted_claim["claim"],
                    lie=False,  # Extracted claims are new, not lies
                    confidence=extracted_claim["confidence"],
                    category=extracted_claim["category"],
                )
        return result


# ========== INTERVIEWER AGENT (Refactored) ========== 
class InterviewerAgent:
    """The main agent for conducting the interview, with integrated nudging."""

    class NextAction(BaseModel):
        action: str
        text: str

    class InterviewerResponse(BaseModel):
        evaluation: str
        updated_covered_topics: List[str]
        next_action: "InterviewerAgent.NextAction"

    class FinalReview(BaseModel):
        overall_summary: str = Field(
            description="Overall summary of the candidate's performance."
        )
        strengths: List[str] = Field(
            description="Bulleted list of candidate's strengths."
        )
        areas_for_improvement: List[str] = Field(
            description="Bulleted list of areas for improvement."
        )
        hiring_recommendation: str = Field(
            description="Hiring recommendation (Strong Hire, Hire, No Hire, etc.)."
        )

    class NudgeContent(BaseModel):
        nudge_text: str
        follow_up_question: str
        severity: str

    def __init__(self, knowledge_db: KnowledgeDatabase, llm_client: ChatCerebras, mode: str = "grilling"):
        self.knowledge_db = knowledge_db
        self.llm = llm_client
        self.active_nudges: Dict[str, Any] = {}
        self.escalation_levels = {
            1: "polite",
            2: "firm", 
            3: "aggressive",
            4: "final_warning",
        }
        
        # Fetch JD data once
        self.jd_requirements = self.knowledge_db.get_jd_requirements_as_string()
        self.jd_responsibilities = self.knowledge_db.get_jd_responsibilities_as_string()

        # Always use grilling mode - no more friendly interviews
        system_prompt = GRILLING_INTERVIEWER_PROMPT

        # Chain for generating questions
        self.question_parser = PydanticOutputParser(
            pydantic_object=self.InterviewerResponse
        )
        self.question_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "user",
                    "CONTEXT:\n- Verified Facts: {facts}\n- Conversation History: {history}\n- Topics Covered: {covered_topics}\n- Candidate's Last Response: {last_response}",
                ),
            ]
        )
        self.question_chain = (
            self.question_prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(sanitize_llm_json_output)
            | self.question_parser
        )

        # Chain for generating nudges
        self.nudge_parser = PydanticOutputParser(pydantic_object=self.NudgeContent)
        self.nudge_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", NUDGE_GENERATION_SYSTEM_PROMPT),
                ("user", "Generate a nudge for the detected lie."),
            ]
        )
        self.nudge_chain = (
            self.nudge_prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(sanitize_llm_json_output)
            | self.nudge_parser
        )

        # Chain for generating a final review
        self.review_parser = PydanticOutputParser(pydantic_object=self.FinalReview)
        self.review_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", FINAL_REVIEW_PROMPT),
                ("user", "TRANSCRIPT:\n{history}"),
            ]
        )
        self.review_chain = (
            self.review_prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(sanitize_llm_json_output)
            | self.review_parser
        )

    async def generate_final_review(self, history: List[Dict]) -> FinalReview:
        """Generates a final review of the candidate after the interview."""
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        return await self.review_chain.ainvoke(
            {
                "history": history_str,
                "format_instructions": self.review_parser.get_format_instructions(),
            }
        )

    async def generate_action(
        self,
        history: List[Dict],
        covered_topics: List[str],
        last_response: str,
    ) -> InterviewerResponse:
        """Generates the next interview action (e.g., asks a question)."""
        facts = self.knowledge_db.get_facts_as_string()
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        return await self.question_chain.ainvoke(
            {
                "facts": facts,
                "jd_requirements": self.jd_requirements,
                "jd_responsibilities": self.jd_responsibilities,
                "history": history_str,
                "covered_topics": ", ".join(covered_topics),
                "last_response": last_response,
                "format_instructions": self.question_parser.get_format_instructions(),
            }
        )

    async def deliver_nudge(self, lie_claim: ClaimAnalysis, tts: InterviewTTS):
        """Generates and speaks a nudge for a detected lie."""
        try:
            claim_key = lie_claim.claim.lower().strip()
            repeat_count = self.active_nudges.get(claim_key, {}).get("count", 0) + 1
            escalation = self.escalation_levels.get(repeat_count, "final_warning")
            nudge_content = await self.nudge_chain.ainvoke(
                {
                    "claim": lie_claim.claim,
                    "confidence": lie_claim.confidence,
                    "reasoning": lie_claim.reasoning,
                    "escalation_level": escalation,
                    "repeat_count": repeat_count,
                    "format_instructions": self.nudge_parser.get_format_instructions(),
                }
            )
            if claim_key not in self.active_nudges:
                self.active_nudges[claim_key] = {"count": 0, "history": []}
            self.active_nudges[claim_key]["count"] += 1
            self.active_nudges[claim_key]["history"].append(nudge_content.nudge_text)
            full_response = (
                f"{nudge_content.nudge_text} {nudge_content.follow_up_question}"
            )
            clean_response = strip_markdown(full_response)
            await tts.speak(clean_response)
        except Exception as e:
            logging.error(f"Error delivering LLM-based nudge: {e}", exc_info=True)
            fallback_text = generate_simple_nudge_text(lie_claim, "polite")
            clean_fallback = strip_markdown(fallback_text)
            await tts.speak(clean_fallback)