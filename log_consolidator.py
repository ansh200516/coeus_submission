#!/usr/bin/env python3
"""
Log Consolidator Script

This script processes the latest log files from both interview systems:
1. Brain/lda/main.py (LDA interview system) - generates interview_summary_*.json files
2. Brain/code interview agent/main.py (Code interview system) - generates performance_*.json files

It extracts and consolidates the following data:
- Summary data from interview logs
- Static knowledge (LinkedIn and resume data)
- Job description data
- Lies detected during interviews
- Candidate scores from code interviews

The output is a new consolidated log file with all extracted information.
"""

import json
import os
import glob
import datetime
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LogConsolidator:
    """
    Main class for consolidating interview log files from both systems.
    """

    def __init__(self, project_root: str) -> None:
        """
        Initialize the log consolidator.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.lda_logs_dir = self.project_root / "old logs"  # LDA logs are in old logs
        self.code_logs_dir = self.project_root / "Brain" / "code interview agent" / "interviews"
        self.output_dir = self.project_root / "consolidated_logs"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized LogConsolidator with project root: {project_root}")
        logger.info(f"LDA logs directory: {self.lda_logs_dir}")
        logger.info(f"Code logs directory: {self.code_logs_dir}")
        logger.info(f"Output directory: {self.output_dir}")

    def find_latest_lda_log(self) -> Optional[Path]:
        """
        Find the latest LDA interview summary log file.
        
        Returns:
            Path to the latest LDA log file, or None if not found
        """
        try:
            pattern = str(self.lda_logs_dir / "interview_summary_*.json")
            lda_files = glob.glob(pattern)
            
            if not lda_files:
                logger.warning(f"No LDA interview summary files found in {self.lda_logs_dir}")
                return None
            
            # Sort by modification time (most recent first)
            latest_file = max(lda_files, key=os.path.getmtime)
            logger.info(f"Found latest LDA log: {os.path.basename(latest_file)}")
            return Path(latest_file)
            
        except Exception as e:
            logger.error(f"Error finding latest LDA log: {e}")
            return None

    def find_latest_code_log(self) -> Optional[Path]:
        """
        Find the latest code interview performance log file.
        
        Returns:
            Path to the latest code interview log file, or None if not found
        """
        try:
            pattern = str(self.code_logs_dir / "performance_*.json")
            code_files = glob.glob(pattern)
            
            if not code_files:
                logger.warning(f"No code interview performance files found in {self.code_logs_dir}")
                return None
            
            # Sort by modification time (most recent first)
            latest_file = max(code_files, key=os.path.getmtime)
            logger.info(f"Found latest code interview log: {os.path.basename(latest_file)}")
            return Path(latest_file)
            
        except Exception as e:
            logger.error(f"Error finding latest code interview log: {e}")
            return None

    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {file_path.name}")
            return data
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None

    def extract_summary_data(self, lda_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract summary data from LDA interview log.
        
        Args:
            lda_data: LDA interview log data
            
        Returns:
            Extracted summary data
        """
        try:
            summary = lda_data.get("summary", {})
            
            extracted_summary = {
                "overall_summary": summary.get("overall_summary", ""),
                "strengths": summary.get("strengths", []),
                "areas_for_improvement": summary.get("areas_for_improvement", []),
                "hiring_recommendation_from_lda": summary.get("hiring_recommendation", "")
            }
            
            logger.info("Successfully extracted summary data from LDA log")
            return extracted_summary
            
        except Exception as e:
            logger.error(f"Error extracting summary data: {e}")
            return {}

    def extract_static_knowledge(self, lda_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract and join static knowledge from LinkedIn and resume sources.
        
        Args:
            lda_data: LDA interview log data
            
        Returns:
            Dictionary with linkedin and resume claims
        """
        try:
            knowledge_base = lda_data.get("knowledge_base", {})
            entries = knowledge_base.get("entries", [])
            
            linkedin_claims = []
            resume_claims = []
            
            for entry in entries:
                source = entry.get("source", "")
                claim = entry.get("claim", "")
                
                if source == "linkedin" and claim:
                    linkedin_claims.append(claim)
                elif source == "resume" and claim:
                    resume_claims.append(claim)
            
            static_knowledge = {
                "linkedin": linkedin_claims,
                "resume": resume_claims
            }
            
            logger.info(f"Extracted {len(linkedin_claims)} LinkedIn claims and {len(resume_claims)} resume claims")
            return static_knowledge
            
        except Exception as e:
            logger.error(f"Error extracting static knowledge: {e}")
            return {"linkedin": [], "resume": []}

    def extract_job_description(self, lda_data: Dict[str, Any]) -> List[str]:
        """
        Extract and join job description data from knowledge base.
        
        Args:
            lda_data: LDA interview log data
            
        Returns:
            List of job description claims
        """
        try:
            knowledge_base = lda_data.get("knowledge_base", {})
            entries = knowledge_base.get("entries", [])
            
            job_description_claims = []
            
            for entry in entries:
                source = entry.get("source", "")
                claim = entry.get("claim", "")
                
                if source == "job_description" and claim:
                    job_description_claims.append(claim)
            
            logger.info(f"Extracted {len(job_description_claims)} job description claims")
            return job_description_claims
            
        except Exception as e:
            logger.error(f"Error extracting job description: {e}")
            return []

    def extract_lies_data(self, lda_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract lies data from LDA interview log.
        
        Args:
            lda_data: LDA interview log data
            
        Returns:
            List of detected lies with details
        """
        try:
            lies = lda_data.get("lies", [])
            
            extracted_lies = []
            for lie in lies:
                if isinstance(lie, dict):
                    extracted_lies.append({
                        "lie": lie.get("lie", ""),
                        "explanation_given_by_candidate": lie.get("explanation_given_by_candidate", ""),
                        "confidence": lie.get("confidence", 0.0),
                        "reasoning": lie.get("reasoning", ""),
                        "category": lie.get("category", "")
                    })
            
            logger.info(f"Extracted {len(extracted_lies)} lies from LDA log")
            return extracted_lies
            
        except Exception as e:
            logger.error(f"Error extracting lies data: {e}")
            return []

    def extract_candidate_scores(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract candidate scores from code interview log.
        
        Args:
            code_data: Code interview log data
            
        Returns:
            Dictionary with candidate scores and performance data
        """
        try:
            candidate_info = code_data.get("candidate", {})
            problem_info = code_data.get("problem", {})
            scores = code_data.get("scores", {})
            time_info = code_data.get("time", {})
            tests = code_data.get("tests", {})
            feedback = code_data.get("feedback", {})
            
            extracted_scores = {
                "candidate": {
                    "name": candidate_info.get("name", ""),
                    "user_id": candidate_info.get("user_id", "")
                },
                "problem": {
                    "id": problem_info.get("id", ""),
                    "title": problem_info.get("title", ""),
                    "difficulty": problem_info.get("difficulty", ""),
                    "language": problem_info.get("language", "")
                },
                "scores": {
                    "final": scores.get("final", 0),
                    "components": scores.get("components", {})
                },
                "time_performance": {
                    "time_allowed_min": time_info.get("time_allowed_min", 0),
                    "time_used_min": time_info.get("time_used_min", 0),
                    "start_time": time_info.get("start", ""),
                    "end_time": time_info.get("end", "")
                },
                "test_results": {
                    "public_tests": tests.get("public", []),
                    "hidden_tests": tests.get("hidden", {})
                },
                "feedback": {
                    "strengths": feedback.get("strengths", []),
                    "weaknesses": feedback.get("weaknesses", []),
                    "recommendation": feedback.get("recommendation", "")
                }
            }
            
            logger.info(f"Extracted scores for candidate: {candidate_info.get('name', 'Unknown')}")
            logger.info(f"Final score: {scores.get('final', 0)}")
            return extracted_scores
            
        except Exception as e:
            logger.error(f"Error extracting candidate scores: {e}")
            return {}

    def calculate_hirability_score(
        self,
        static_knowledge: Dict[str, List[str]],
        job_description: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate hirability score based on candidate's LinkedIn/resume data against job description.
        
        Args:
            static_knowledge: LinkedIn and resume data
            job_description: Job description requirements
            
        Returns:
            Dictionary with hirability score and breakdown
        """
        try:
            # Combine all candidate data
            all_candidate_data = []
            all_candidate_data.extend(static_knowledge.get("linkedin", []))
            all_candidate_data.extend(static_knowledge.get("resume", []))
            
            # Convert to lowercase for better matching
            candidate_text = " ".join(all_candidate_data).lower()
            job_desc_text = " ".join(job_description).lower()
            
            # Define scoring categories with keywords and weights
            scoring_criteria = {
                "technical_skills": {
                    "weight": 0.30,
                    "keywords": [
                        "python", "javascript", "typescript", "react", "vue.js", "angular",
                        "node.js", "flask", "django", "java", "c++", "sql", "nosql",
                        "mongodb", "postgresql", "mysql", "api", "rest", "graphql",
                        "aws", "gcp", "azure", "cloud", "docker", "kubernetes",
                        "git", "ci/cd", "devops", "microservices", "html", "css"
                    ]
                },
                "ai_ml_experience": {
                    "weight": 0.25,
                    "keywords": [
                        "machine learning", "artificial intelligence", "ai", "ml",
                        "pytorch", "tensorflow", "deep learning", "neural network",
                        "data science", "nlp", "computer vision", "model", "algorithm",
                        "pandas", "numpy", "scikit-learn", "keras", "opencv"
                    ]
                },
                "experience_level": {
                    "weight": 0.20,
                    "keywords": [
                        "senior", "lead", "architect", "manager", "years", "experience",
                        "internship", "full-time", "engineer", "developer", "software",
                        "project", "team", "leadership", "mentoring"
                    ]
                },
                "education_background": {
                    "weight": 0.15,
                    "keywords": [
                        "computer science", "software engineering", "engineering",
                        "bachelor", "master", "phd", "degree", "university", "college",
                        "iit", "mit", "stanford", "gpa", "coursework", "certification"
                    ]
                },
                "soft_skills": {
                    "weight": 0.10,
                    "keywords": [
                        "communication", "collaboration", "teamwork", "problem solving",
                        "leadership", "agile", "scrum", "project management",
                        "analytical", "creative", "innovation", "documentation"
                    ]
                }
            }
            
            # Calculate scores for each category
            category_scores = {}
            detailed_matches = {}
            
            for category, criteria in scoring_criteria.items():
                keywords = criteria["keywords"]
                matches = []
                score = 0
                
                for keyword in keywords:
                    # Check if keyword appears in candidate data
                    if keyword in candidate_text:
                        matches.append(keyword)
                        # Also check if it's mentioned in job description for relevance
                        if keyword in job_desc_text:
                            score += 2  # Higher score for job-relevant skills
                        else:
                            score += 1  # Lower score for additional skills
                
                # Normalize score (max 100 per category)
                max_possible = len(keywords) * 2
                normalized_score = min(100, (score / max_possible) * 100) if max_possible > 0 else 0
                
                category_scores[category] = normalized_score
                detailed_matches[category] = {
                    "score": normalized_score,
                    "matches": matches,
                    "match_count": len(matches)
                }
            
            # Calculate weighted overall score
            overall_score = sum(
                category_scores[category] * criteria["weight"]
                for category, criteria in scoring_criteria.items()
            )
            
            # Determine hiring recommendation based on score
            if overall_score >= 80:
                recommendation = "Strong Hire"
            elif overall_score >= 65:
                recommendation = "Hire"
            elif overall_score >= 50:
                recommendation = "Weak Hire"
            elif overall_score >= 35:
                recommendation = "Weak No Hire"
            else:
                recommendation = "No Hire"
            
            # Calculate experience years (rough estimate)
            experience_indicators = re.findall(r'(\d+)\s*(?:years?|yrs?|mos?|months?)', candidate_text)
            estimated_experience = 0
            if experience_indicators:
                # Sum up all numeric experience indicators and convert to years
                for exp in experience_indicators:
                    exp_num = int(exp)
                    if "mo" in candidate_text or "month" in candidate_text:
                        estimated_experience += exp_num / 12
                    else:
                        estimated_experience += exp_num
            
            hirability_data = {
                "overall_score": round(overall_score, 2),
                "recommendation": recommendation,
                "category_breakdown": detailed_matches,
                "estimated_experience_years": round(estimated_experience, 1),
                "scoring_methodology": {
                    "technical_skills": f"{scoring_criteria['technical_skills']['weight']*100}%",
                    "ai_ml_experience": f"{scoring_criteria['ai_ml_experience']['weight']*100}%",
                    "experience_level": f"{scoring_criteria['experience_level']['weight']*100}%",
                    "education_background": f"{scoring_criteria['education_background']['weight']*100}%",
                    "soft_skills": f"{scoring_criteria['soft_skills']['weight']*100}%"
                },
                "analysis_summary": {
                    "total_linkedin_claims": len(static_knowledge.get("linkedin", [])),
                    "total_resume_claims": len(static_knowledge.get("resume", [])),
                    "job_requirements_analyzed": len(job_description)
                }
            }
            
            logger.info(f"Calculated hirability score: {overall_score:.2f} ({recommendation})")
            return hirability_data
            
        except Exception as e:
            logger.error(f"Error calculating hirability score: {e}")
            return {
                "overall_score": 0,
                "recommendation": "Unable to Calculate",
                "error": str(e)
            }

    def create_consolidated_log(
        self,
        summary_data: Dict[str, Any],
        static_knowledge: Dict[str, List[str]],
        job_description: List[str],
        lies_data: List[Dict[str, Any]],
        candidate_scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create the consolidated log structure.
        
        Args:
            summary_data: Interview summary data
            static_knowledge: LinkedIn and resume data
            job_description: Job description claims
            lies_data: Detected lies data
            candidate_scores: Code interview scores
            
        Returns:
            Consolidated log data structure
        """
        try:
            # Calculate hirability score
            hirability_score = self.calculate_hirability_score(static_knowledge, job_description)
            
            consolidated_log = {
                "metadata": {
                    "consolidation_timestamp": datetime.datetime.now().isoformat(),
                    "consolidator_version": "1.0.0",
                    "sources": {
                        "lda_interview": True if summary_data else False,
                        "code_interview": True if candidate_scores else False
                    }
                },
                "summary": summary_data,
                "static_knowledge": static_knowledge,
                "job_description": job_description,
                "lies": lies_data,
                "candidate_scores": candidate_scores,
                "hirability_score": hirability_score
            }
            
            logger.info("Successfully created consolidated log structure")
            return consolidated_log
            
        except Exception as e:
            logger.error(f"Error creating consolidated log: {e}")
            return {}

    def save_consolidated_log(self, consolidated_data: Dict[str, Any]) -> Optional[Path]:
        """
        Save the consolidated log to a file.
        
        Args:
            consolidated_data: The consolidated log data
            
        Returns:
            Path to the saved file, or None if failed
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"consolidated_interview_log_{timestamp}.json"
            output_path = self.output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Consolidated log saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving consolidated log: {e}")
            return None

    def process_logs(self) -> Optional[Path]:
        """
        Main method to process and consolidate logs from both systems.
        
        Returns:
            Path to the consolidated log file, or None if failed
        """
        logger.info("Starting log consolidation process...")
        
        # Find latest log files
        latest_lda_log = self.find_latest_lda_log()
        latest_code_log = self.find_latest_code_log()
        
        if not latest_lda_log and not latest_code_log:
            logger.error("No log files found from either system")
            return None
        
        # Load log files
        lda_data = {}
        code_data = {}
        
        if latest_lda_log:
            lda_data = self.load_json_file(latest_lda_log) or {}
        
        if latest_code_log:
            code_data = self.load_json_file(latest_code_log) or {}
        
        # Extract data from logs
        summary_data = self.extract_summary_data(lda_data) if lda_data else {}
        static_knowledge = self.extract_static_knowledge(lda_data) if lda_data else {"linkedin": [], "resume": []}
        job_description = self.extract_job_description(lda_data) if lda_data else []
        lies_data = self.extract_lies_data(lda_data) if lda_data else []
        candidate_scores = self.extract_candidate_scores(code_data) if code_data else {}
        
        # Create consolidated log
        consolidated_log = self.create_consolidated_log(
            summary_data,
            static_knowledge,
            job_description,
            lies_data,
            candidate_scores
        )
        
        if not consolidated_log:
            logger.error("Failed to create consolidated log")
            return None
        
        # Save consolidated log
        output_path = self.save_consolidated_log(consolidated_log)
        
        if output_path:
            logger.info("Log consolidation completed successfully!")
            self._print_summary(consolidated_log)
        
        return output_path

    def _print_summary(self, consolidated_log: Dict[str, Any]) -> None:
        """
        Print a summary of the consolidated log.
        
        Args:
            consolidated_log: The consolidated log data
        """
        print("\n" + "="*60)
        print("📊 CONSOLIDATED LOG SUMMARY")
        print("="*60)
        
        metadata = consolidated_log.get("metadata", {})
        sources = metadata.get("sources", {})
        
        print(f"🕒 Consolidation Time: {metadata.get('consolidation_timestamp', 'Unknown')}")
        print(f"📁 Sources Available:")
        print(f"   - LDA Interview: {'✅' if sources.get('lda_interview') else '❌'}")
        print(f"   - Code Interview: {'✅' if sources.get('code_interview') else '❌'}")
        
        # Summary stats
        summary = consolidated_log.get("summary", {})
        static_knowledge = consolidated_log.get("static_knowledge", {})
        job_description = consolidated_log.get("job_description", [])
        lies = consolidated_log.get("lies", [])
        scores = consolidated_log.get("candidate_scores", {})
        
        print(f"\n📋 Data Summary:")
        print(f"   - LinkedIn Claims: {len(static_knowledge.get('linkedin', []))}")
        print(f"   - Resume Claims: {len(static_knowledge.get('resume', []))}")
        print(f"   - Job Description Claims: {len(job_description)}")
        print(f"   - Lies Detected: {len(lies)}")
        
        # Display hirability score
        hirability = consolidated_log.get("hirability_score", {})
        if hirability:
            print(f"   - Hirability Score: {hirability.get('overall_score', 0)}/100 ({hirability.get('recommendation', 'Unknown')})")
        
        if scores:
            candidate_info = scores.get("candidate", {})
            score_info = scores.get("scores", {})
            print(f"   - Code Interview Candidate: {candidate_info.get('name', 'Unknown')}")
            print(f"   - Final Score: {score_info.get('final', 0)}")
        
        print("="*60)


def find_project_root() -> Optional[str]:
    """
    Find the project root directory by looking for specific marker files.
    
    Returns:
        Path to project root or None if not found
    """
    current_dir = Path.cwd()
    
    # Look for marker files that indicate project root
    markers = ["pyproject.toml", "requirements.txt", "README.md"]
    
    # Search up the directory tree
    for parent in [current_dir] + list(current_dir.parents):
        if any((parent / marker).exists() for marker in markers):
            return str(parent)
    
    return None


def main() -> None:
    """
    Main entry point for the log consolidator script.
    """
    print("🔄 Interview Log Consolidator")
    print("=" * 50)
    
    # Find project root
    project_root = find_project_root()
    if not project_root:
        print("❌ Could not find project root directory")
        print("   Please run this script from within the project directory")
        return
    
    print(f"📁 Project root: {project_root}")
    
    # Initialize consolidator
    consolidator = LogConsolidator(project_root)
    
    # Process logs
    output_path = consolidator.process_logs()
    
    if output_path:
        print(f"\n✅ Consolidation completed successfully!")
        print(f"📄 Output file: {output_path}")
    else:
        print(f"\n❌ Consolidation failed!")
        print("   Check the logs above for error details")


if __name__ == "__main__":
    main()
