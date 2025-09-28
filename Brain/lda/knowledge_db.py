import json
import os
import glob
from typing import Dict, List, Any, Optional
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
    
    def auto_load_latest_candidate_data(self, project_root: str, candidate_name: Optional[str] = None) -> Dict[str, str]:
        """
        Automatically finds and loads the latest LinkedIn and resume data for a candidate.
        
        Args:
            project_root: The project root directory
            candidate_name: Optional candidate name to filter files
            
        Returns:
            Dictionary with paths of loaded files
        """
        logs_dir = os.path.join(project_root, "logs")
        loaded_files = {"linkedin": None, "resume": None}
        
        if not os.path.exists(logs_dir):
            print(f"Logs directory not found: {logs_dir}")
            return loaded_files
        
        # Find latest LinkedIn file
        linkedin_pattern = os.path.join(logs_dir, "person_*.json")
        linkedin_files = glob.glob(linkedin_pattern)
        
        if candidate_name:
            # Filter by candidate name
            safe_candidate_name = candidate_name.replace(" ", "_").replace(".", "_")
            linkedin_files = [f for f in linkedin_files if safe_candidate_name.lower() in os.path.basename(f).lower()]
        
        if linkedin_files:
            # Get the most recent LinkedIn file
            latest_linkedin = max(linkedin_files, key=os.path.getmtime)
            self._parse_linkedin_data(latest_linkedin)
            loaded_files["linkedin"] = latest_linkedin
            print(f"✅ Loaded LinkedIn data from: {os.path.basename(latest_linkedin)}")
        else:
            print("⚠️  No LinkedIn data files found")
        
        # Find latest resume file
        resume_pattern = os.path.join(logs_dir, "resume_*.json")
        resume_files = glob.glob(resume_pattern)
        
        if resume_files:
            # Get the most recent resume file
            latest_resume = max(resume_files, key=os.path.getmtime)
            self._parse_resume_data(latest_resume)
            loaded_files["resume"] = latest_resume
            print(f"✅ Loaded resume data from: {os.path.basename(latest_resume)}")
        else:
            print("⚠️  No resume data files found")
            
        return loaded_files
    
    def load_combined_candidate_data(self, combined_file_path: str) -> None:
        """
        Load candidate data from a combined JSON file (from unified_scraper.py).
        
        Args:
            combined_file_path: Path to the combined candidate data JSON file
        """
        try:
            with open(combined_file_path, 'r') as f:
                data = json.load(f)
            
            print(f"📖 Loading combined candidate data from: {os.path.basename(combined_file_path)}")
            
            # Extract LinkedIn data if present
            linkedin_data = data.get('linkedin_data')
            if linkedin_data:
                print("  📱 Processing LinkedIn data...")
                self._parse_linkedin_data_dict(linkedin_data)
            
            # Extract resume data if present
            resume_data = data.get('resume_data')
            if resume_data:
                print("  📄 Processing resume data...")
                self._parse_resume_data_dict(resume_data)
            
            candidate_name = data.get('candidate_name', 'Unknown')
            metadata = data.get('metadata', {})
            
            print(f"  ✅ Loaded data for: {candidate_name}")
            print(f"  📊 LinkedIn entries: {metadata.get('linkedin_entries', 0)}")
            print(f"  📊 Resume entries: {metadata.get('resume_entries', 0)}")
            print(f"  📊 Total raw entries: {metadata.get('total_entries', 0)}")
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not process combined candidate file {combined_file_path}: {e}")
    
    def auto_load_latest_combined_data(self, load_data: bool = True) -> Optional[str]:
        """
        Automatically find and load the latest combined candidate data file.
        
        Args:
            load_data: If True, loads the data into the knowledge base. If False, just returns the file path.
        
        Returns:
            Path to the file (loaded or found), or None if no file found
        """
        lda_logs_dir = os.path.join(os.path.dirname(__file__), "lda_logs")
        
        if not os.path.exists(lda_logs_dir):
            print(f"LDA logs directory not found: {lda_logs_dir}")
            return None
        
        # Find combined data files
        combined_pattern = os.path.join(lda_logs_dir, "combined_candidate_data_*.json")
        combined_files = glob.glob(combined_pattern)
        
        if combined_files:
            # Get the most recent combined file
            latest_combined = max(combined_files, key=os.path.getmtime)
            
            if load_data:
                self.load_combined_candidate_data(latest_combined)
                print(f"✅ Loaded latest combined data: {os.path.basename(latest_combined)}")
            
            return latest_combined
        else:
            print("⚠️  No combined candidate data files found in lda_logs")
            return None
    
    def _parse_linkedin_data_dict(self, data: Dict[str, Any]) -> None:
        """Parse LinkedIn data from a dictionary (used by combined data loader)."""
        # Extract personal information
        if data.get('name'):
            self._add_entry(data['name'], 'linkedin', 'personal', {'field': 'name'})
        
        if data.get('about'):
            self._add_entry(data['about'], 'linkedin', 'personal', {'field': 'about'})
        
        # Extract work experiences
        for exp in data.get('experiences', []):
            if exp.get('position_title') and exp.get('institution_name'):
                exp_text = f"{exp['position_title']} at {exp['institution_name']}"
                if exp.get('duration'):
                    exp_text += f" ({exp['duration']})"
                if exp.get('location'):
                    exp_text += f" - {exp['location']}"
                self._add_entry(exp_text, 'linkedin', 'experience', {
                    'company': exp.get('institution_name'),
                    'position': exp.get('position_title'),
                    'duration': exp.get('duration'),
                    'location': exp.get('location')
                })
            
            # Extract key accomplishments from experience descriptions
            if exp.get('description'):
                desc = exp['description']
                sentences = desc.split('. ')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 30 and ('developed' in sentence.lower() or 
                                               'built' in sentence.lower() or 
                                               'implemented' in sentence.lower() or
                                               'enhanced' in sentence.lower() or
                                               'achieved' in sentence.lower()):
                        self._add_entry(sentence, 'linkedin', 'achievement', {
                            'company': exp.get('institution_name'),
                            'position': exp.get('position_title')
                        })
        
        # Extract education
        for edu in data.get('educations', []):
            if edu.get('degree') and edu.get('institution_name'):
                edu_text = f"{edu['degree']} from {edu['institution_name']}"
                if edu.get('from_date') and edu.get('to_date'):
                    edu_text += f" ({edu['from_date']} - {edu['to_date']})"
                self._add_entry(edu_text, 'linkedin', 'education', {
                    'degree': edu.get('degree'),
                    'institution': edu.get('institution_name'),
                    'from_date': edu.get('from_date'),
                    'to_date': edu.get('to_date')
                })
                
                # Extract GPA if mentioned in description
                if edu.get('description') and 'grade' in edu['description'].lower():
                    grade_match = None
                    desc = edu['description'].lower()
                    if 'grade:' in desc:
                        grade_part = desc.split('grade:')[1].strip()
                        grade_match = grade_part.split()[0] if grade_part else None
                    if grade_match:
                        self._add_entry(f"GPA: {grade_match} at {edu.get('institution_name', 'institution')}", 
                                      'linkedin', 'education', {'type': 'gpa'})
        
        # Extract skills
        for skill in data.get('skills', []):
            if skill.get('name'):
                self._add_entry(skill['name'], 'linkedin', 'skill', {
                    'endorsements': skill.get('endorsements', 0)
                })
        
        # Extract projects
        for project in data.get('projects', []):
            if project.get('title'):
                proj_text = project['title']
                if project.get('associated_with'):
                    proj_text += f" ({project['associated_with']})"
                self._add_entry(proj_text, 'linkedin', 'project', {
                    'title': project.get('title'),
                    'timeframe': project.get('associated_with'),
                    'url': project.get('url')
                })
        
        # Extract licenses and certifications
        for license in data.get('licenses', []):
            if license.get('name'):
                cert_text = license['name']
                if license.get('issuing_organization'):
                    cert_text += f" from {license['issuing_organization']}"
                if license.get('issue_date'):
                    cert_text += f" ({license['issue_date']})"
                self._add_entry(cert_text, 'linkedin', 'certification', {
                    'name': license.get('name'),
                    'organization': license.get('issuing_organization'),
                    'date': license.get('issue_date'),
                    'credential_id': license.get('credential_id')
                })
        
        # Extract honors and achievements
        for honor in data.get('honors', []):
            if honor.get('title'):
                honor_text = honor['title']
                if honor.get('issuer'):
                    honor_text += f" - {honor['issuer']}"
                self._add_entry(honor_text, 'linkedin', 'achievement', {
                    'title': honor.get('title'),
                    'issuer': honor.get('issuer'),
                    'description': honor.get('description')
                })
    
    def _parse_resume_data_dict(self, data: Dict[str, Any]) -> None:
        """Parse resume data from a dictionary (used by combined data loader)."""
        sections = data.get('sections', {})
        
        # Extract name from header section
        header_data = sections.get('HEADER', [])
        if header_data:
            name = header_data[0] if header_data else None
            if name and name.strip():
                self._add_entry(name.strip(), 'resume', 'personal', {'field': 'name'})
        
        # Extract education from IIT COURSE section
        iit_course_data = sections.get('IIT COURSE', [])
        academic_data = sections.get('ACADEMIC DETAILS', [])
        all_education_data = iit_course_data + academic_data
        
        for item in all_education_data:
            item = item.strip()
            if 'B.Tech' in item or 'Bachelor' in item or 'Master' in item or 'PhD' in item:
                self._add_entry(item, 'resume', 'education', {'type': 'degree'})
            elif 'Indian Institute of Technology' in item or 'IIT' in item:
                self._add_entry(item, 'resume', 'education', {'type': 'institution'})
            elif item.replace('.', '').replace(',', '').isdigit() or ('.' in item and len(item.split('.')) == 2):
                try:
                    float(item.replace(',', ''))
                    self._add_entry(f"GPA: {item}", 'resume', 'education', {'type': 'gpa'})
                except ValueError:
                    pass
        
        # Extract internships and work experience
        internship_data = sections.get('INTERNSHIPS', [])
        for item in internship_data:
            item = item.strip()
            if len(item) > 10:
                if ('Atlassian' in item or 'UNSW' in item or 'University' in item or 
                    'Intern' in item or 'Research' in item or 'Technical' in item):
                    self._add_entry(item, 'resume', 'experience', {'source': 'internships'})
        
        # Extract projects
        project_data = sections.get('PROJECTS', [])
        for item in project_data:
            item = item.strip()
            if len(item) > 15:
                if ('AI' in item or 'Game' in item or 'Stock' in item or 'Search' in item or 
                    'Database' in item or 'developed' in item.lower() or 'built' in item.lower()):
                    self._add_entry(item, 'resume', 'project', {'source': 'projects'})
        
        # Extract technical skills
        skills_data = sections.get('TECHNICAL SKILLS', [])
        for item in skills_data:
            item = item.strip()
            if len(item) > 3 and ':' not in item:
                skills = []
                if ',' in item:
                    skills = [s.strip() for s in item.split(',')]
                elif ';' in item:
                    skills = [s.strip() for s in item.split(';')]
                else:
                    skills = [item]
                
                for skill in skills:
                    skill = skill.strip()
                    if len(skill) > 2 and skill.lower() not in ['software', 'tools', 'languages']:
                        self._add_entry(skill, 'resume', 'skill', {'source': 'technical_skills'})

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

    def _parse_linkedin_data(self, file_path: str) -> None:
        """Parses data from a LinkedIn JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract personal information
            if data.get('name'):
                self._add_entry(data['name'], 'linkedin', 'personal', {'field': 'name'})
            
            if data.get('about'):
                self._add_entry(data['about'], 'linkedin', 'personal', {'field': 'about'})
            
            # Extract work experiences
            for exp in data.get('experiences', []):
                if exp.get('position_title') and exp.get('institution_name'):
                    exp_text = f"{exp['position_title']} at {exp['institution_name']}"
                    if exp.get('duration'):
                        exp_text += f" ({exp['duration']})"
                    if exp.get('location'):
                        exp_text += f" - {exp['location']}"
                    self._add_entry(exp_text, 'linkedin', 'experience', {
                        'company': exp.get('institution_name'),
                        'position': exp.get('position_title'),
                        'duration': exp.get('duration'),
                        'location': exp.get('location')
                    })
                
                # Extract key accomplishments from experience descriptions
                if exp.get('description'):
                    desc = exp['description']
                    # Split description into meaningful chunks and extract key achievements
                    sentences = desc.split('. ')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 30 and ('developed' in sentence.lower() or 
                                                   'built' in sentence.lower() or 
                                                   'implemented' in sentence.lower() or
                                                   'enhanced' in sentence.lower() or
                                                   'achieved' in sentence.lower()):
                            self._add_entry(sentence, 'linkedin', 'achievement', {
                                'company': exp.get('institution_name'),
                                'position': exp.get('position_title')
                            })
            
            # Extract education
            for edu in data.get('educations', []):
                if edu.get('degree') and edu.get('institution_name'):
                    edu_text = f"{edu['degree']} from {edu['institution_name']}"
                    if edu.get('from_date') and edu.get('to_date'):
                        edu_text += f" ({edu['from_date']} - {edu['to_date']})"
                    self._add_entry(edu_text, 'linkedin', 'education', {
                        'degree': edu.get('degree'),
                        'institution': edu.get('institution_name'),
                        'from_date': edu.get('from_date'),
                        'to_date': edu.get('to_date')
                    })
                    
                    # Extract GPA if mentioned in description
                    if edu.get('description') and 'grade' in edu['description'].lower():
                        grade_match = None
                        desc = edu['description'].lower()
                        if 'grade:' in desc:
                            grade_part = desc.split('grade:')[1].strip()
                            grade_match = grade_part.split()[0] if grade_part else None
                        if grade_match:
                            self._add_entry(f"GPA: {grade_match} at {edu.get('institution_name', 'institution')}", 
                                          'linkedin', 'education', {'type': 'gpa'})
            
            # Extract skills
            for skill in data.get('skills', []):
                if skill.get('name'):
                    self._add_entry(skill['name'], 'linkedin', 'skill', {
                        'endorsements': skill.get('endorsements', 0)
                    })
            
            # Extract projects
            for project in data.get('projects', []):
                if project.get('title'):
                    proj_text = project['title']
                    if project.get('associated_with'):
                        proj_text += f" ({project['associated_with']})"
                    self._add_entry(proj_text, 'linkedin', 'project', {
                        'title': project.get('title'),
                        'timeframe': project.get('associated_with'),
                        'url': project.get('url')
                    })
                    
                    # Extract key technologies from project description
                    if project.get('description'):
                        desc = project['description']
                        # Look for technology mentions
                        tech_keywords = ['python', 'react', 'javascript', 'ai', 'ml', 'machine learning', 
                                       'opencv', 'flask', 'django', 'tensorflow', 'pytorch']
                        for tech in tech_keywords:
                            if tech.lower() in desc.lower():
                                self._add_entry(f"Experience with {tech.title()}", 'linkedin', 'skill', 
                                              {'source': 'project', 'project': project.get('title')})
            
            # Extract licenses and certifications
            for license in data.get('licenses', []):
                if license.get('name'):
                    cert_text = license['name']
                    if license.get('issuing_organization'):
                        cert_text += f" from {license['issuing_organization']}"
                    if license.get('issue_date'):
                        cert_text += f" ({license['issue_date']})"
                    self._add_entry(cert_text, 'linkedin', 'certification', {
                        'name': license.get('name'),
                        'organization': license.get('issuing_organization'),
                        'date': license.get('issue_date'),
                        'credential_id': license.get('credential_id')
                    })
            
            # Extract honors and achievements
            for honor in data.get('honors', []):
                if honor.get('title'):
                    honor_text = honor['title']
                    if honor.get('issuer'):
                        honor_text += f" - {honor['issuer']}"
                    self._add_entry(honor_text, 'linkedin', 'achievement', {
                        'title': honor.get('title'),
                        'issuer': honor.get('issuer'),
                        'description': honor.get('description')
                    })
            
            print(f"Successfully processed LinkedIn data from {file_path}")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not process LinkedIn file {file_path}: {e}")

    def _parse_resume_data(self, file_path: str) -> None:
        """Parses data from a resume JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            sections = data.get('sections', {})
            
            # Extract name from header section
            header_data = sections.get('HEADER', [])
            if header_data:
                name = header_data[0] if header_data else None
                if name and name.strip():
                    self._add_entry(name.strip(), 'resume', 'personal', {'field': 'name'})
            
            # Extract education from IIT COURSE section
            iit_course_data = sections.get('IIT COURSE', [])
            academic_data = sections.get('ACADEMIC DETAILS', [])
            all_education_data = iit_course_data + academic_data
            
            for item in all_education_data:
                item = item.strip()
                if 'B.Tech' in item or 'Bachelor' in item or 'Master' in item or 'PhD' in item:
                    self._add_entry(item, 'resume', 'education', {'type': 'degree'})
                elif 'Indian Institute of Technology' in item or 'IIT' in item:
                    self._add_entry(item, 'resume', 'education', {'type': 'institution'})
                elif item.replace('.', '').replace(',', '').isdigit() or ('.' in item and len(item.split('.')) == 2):
                    # Looks like a GPA/grade
                    try:
                        float(item.replace(',', ''))
                        self._add_entry(f"GPA: {item}", 'resume', 'education', {'type': 'gpa'})
                    except ValueError:
                        pass
            
            # Extract internships and work experience
            internship_data = sections.get('INTERNSHIPS', [])
            for item in internship_data:
                item = item.strip()
                if len(item) > 10:  # Skip bullet points and short items
                    # Look for company names and positions
                    if ('Atlassian' in item or 'UNSW' in item or 'University' in item or 
                        'Intern' in item or 'Research' in item or 'Technical' in item):
                        self._add_entry(item, 'resume', 'experience', {'source': 'internships'})
            
            # Extract projects
            project_data = sections.get('PROJECTS', [])
            for item in project_data:
                item = item.strip()
                if len(item) > 15:  # Skip bullet points
                    # Look for project indicators
                    if ('AI' in item or 'Game' in item or 'Stock' in item or 'Search' in item or 
                        'Database' in item or 'developed' in item.lower() or 'built' in item.lower()):
                        self._add_entry(item, 'resume', 'project', {'source': 'projects'})
            
            # Extract technical skills
            skills_data = sections.get('TECHNICAL SKILLS', [])
            for item in skills_data:
                item = item.strip()
                if len(item) > 3 and ':' not in item:  # Skip category headers
                    # Split by common delimiters
                    skills = []
                    if ',' in item:
                        skills = [s.strip() for s in item.split(',')]
                    elif ';' in item:
                        skills = [s.strip() for s in item.split(';')]
                    else:
                        skills = [item]
                    
                    for skill in skills:
                        skill = skill.strip()
                        if len(skill) > 2 and skill.lower() not in ['software', 'tools', 'languages']:
                            self._add_entry(skill, 'resume', 'skill', {'source': 'technical_skills'})
            
            # Extract achievements and positions
            positions_data = sections.get('POSITIONS OF RESPONSIBILITY', [])
            for item in positions_data:
                item = item.strip()
                if len(item) > 10:
                    if ('Technical' in item or 'Secretary' in item or 'Coordinator' in item or 
                        'Head' in item or 'Executive' in item):
                        self._add_entry(item, 'resume', 'achievement', {'source': 'positions'})
            
            # Extract scholastic achievements
            achievements_data = sections.get('SCHOLASTIC ACHIEVEMENTS', [])
            for item in achievements_data:
                item = item.strip()
                if len(item) > 10:
                    if ('Award' in item or 'Merit' in item or 'top' in item or 'rating' in item or 
                        'rank' in item.lower() or 'position' in item.lower()):
                        self._add_entry(item, 'resume', 'achievement', {'source': 'scholastic'})
            
            # Extract qualifying exam achievements
            qualifying_data = sections.get('QUALIFYING EXAM', [])
            for item in qualifying_data:
                item = item.strip()
                if len(item) > 10:
                    if ('JEE' in item or 'rank' in item.lower() or 'position' in item.lower() or 
                        'Mathemania' in item or 'Minor' in item):
                        self._add_entry(item, 'resume', 'achievement', {'source': 'qualifying_exams'})
            
            # Extract courses
            courses_data = sections.get('COURSES DONE', [])
            for item in courses_data:
                item = item.strip()
                if len(item) > 5:
                    # Split course names by common delimiters
                    courses = []
                    if ',' in item:
                        courses = [c.strip() for c in item.split(',')]
                    elif '&' in item:
                        courses = [c.strip() for c in item.split('&')]
                    else:
                        courses = [item]
                    
                    for course in courses:
                        course = course.strip()
                        if len(course) > 5:
                            self._add_entry(course, 'resume', 'education', {'type': 'course'})
            
            print(f"Successfully processed resume data from {file_path}")

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
