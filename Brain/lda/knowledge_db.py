import json
from typing import Dict, List, Any
from pydantic import BaseModel

from jd_parser import parse_job_description_with_llm


class KnowledgeEntry(BaseModel):
    """Represents a single piece of factual information."""
    claim: str
    source: str  # e.g., "resume", "linkedin", "interview"
    category: str  # e.g., "experience", "education", "skill"
    metadata: Dict[str, Any] = {}

class KnowledgeDatabase:
    """A database to store, manage, and query factual claims from various sources."""

    def __init__(self):
        """Initializes the KnowledgeDatabase with an empty list of entries."""
        self.entries: List[KnowledgeEntry] = []

    def load_from_files(self, linkedin_file: str, resume_file: str):
        """Loads data from LinkedIn and resume JSON files."""
        if linkedin_file:
            self._parse_linkedin_data(linkedin_file)
        if resume_file:
            self._parse_resume_data(resume_file)

    async def load_job_description(self, jd_file_path: str) -> None:
        """Reads a job description file and uses an LLM to parse it into the KB."""
        try:
            with open(jd_file_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
            
            if not jd_text.strip():
                return

            parsed_data = await parse_job_description_with_llm(jd_text)

            for category, items in parsed_data.items():
                for item in items:
                    self._add_entry(
                        claim=item,
                        source="job_description",
                        category=category.rstrip('s')
                    )
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error processing job description: {e}")

    def _add_entry(self, claim: str, source: str, category: str, metadata: Dict = None):
        """Adds a new entry to the knowledge base."""
        entry = KnowledgeEntry(
            claim=claim,
            source=source,
            category=category,
            metadata=metadata or {},
        )
        self.entries.append(entry)

    def _parse_linkedin_data(self, file_path: str):
        """Parses data from a LinkedIn JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if data.get('name'):
                self._add_entry(data['name'], 'linkedin', 'personal', {'field': 'name'})

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not process LinkedIn file {file_path}: {e}")

    def _parse_resume_data(self, file_path: str):
        """Parses data from a resume JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if 'name' in data.get('personal', {}):
                 self._add_entry(data['personal']['name'], 'resume', 'personal', {'field': 'name'})

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not process Resume file {file_path}: {e}")

    def add_interview_claim(self, claim: str, lie: bool, confidence: float, category: str):
        """Adds a claim made during the interview to the knowledge base."""
        self._add_entry(
            claim=claim,
            source="interview",
            category=category,
            metadata={"lie": lie, "confidence": confidence}
        )

    def get_candidate_name(self) -> str:
        """Retrieves the candidate's name from the knowledge base."""
        for entry in self.entries:
            if entry.category == 'personal' and entry.metadata.get('field') == 'name':
                return entry.claim.split()[0]  # Return first name
        return "Candidate" # Fallback name

    def get_facts_as_string(self) -> str:
        """Returns all facts as a formatted string."""
        return "\n".join([f"✓ {entry.claim}" for entry in self.entries])

    def get_jd_requirements_as_string(self) -> str:
        """Returns all job description requirements as a formatted string."""
        return "\n".join([f"- {entry.claim}" for entry in self.entries if entry.category == 'requirement'])

    def get_jd_responsibilities_as_string(self) -> str:
        """Returns all job description responsibilities as a formatted string."""
        return "\n".join([f"- {entry.claim}" for entry in self.entries if entry.category == 'responsibility'])
        
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the knowledge base to a dictionary."""
        return {"entries": [entry.dict() for entry in self.entries]}
