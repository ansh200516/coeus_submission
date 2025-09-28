#!/usr/bin/env python3
"""
Integration module for existing LinkedIn scraper and resume parser.
This module provides functions to run the existing scrapers and integrate their output with the knowledge base.
"""

import os
import sys
import subprocess
import asyncio
import tempfile
from typing import Optional, Dict, Any
import json
from pathlib import Path

from knowledge_db import KnowledgeDatabase


class ScraperIntegration:
    """Integration class for existing LinkedIn scraper and resume parser."""
    
    def __init__(self, project_root: str):
        """
        Initialize the scraper integration.
        
        Args:
            project_root: The root directory of the project
        """
        self.project_root = project_root
        self.logs_dir = os.path.join(project_root, "logs")
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
    
    async def scrape_linkedin_profile(self, linkedin_url: str, email: str, password: str) -> Optional[str]:
        """
        Run the existing LinkedIn scraper for a given profile.
        
        Args:
            linkedin_url: The LinkedIn profile URL to scrape
            email: LinkedIn login email
            password: LinkedIn login password
            
        Returns:
            Path to the generated JSON file, or None if failed
        """
        print(f"🔍 Scraping LinkedIn profile: {linkedin_url}")
        
        try:
            # Modify the linkdin_scrapper.py to accept URL as argument
            scraper_path = os.path.join(self.project_root, "linkdin_scrapper.py")
            
            # Create a temporary modified version that accepts LinkedIn URL as argument
            temp_scraper = await self._create_temp_linkedin_scraper(scraper_path, linkedin_url)
            
            # Set environment variables
            env = os.environ.copy()
            env["LINKEDIN_EMAIL"] = email
            env["LINKEDIN_PASSW"] = password
            
            # Run the scraper
            result = subprocess.run(
                [sys.executable, temp_scraper],
                env=env,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Clean up temporary file
            os.unlink(temp_scraper)
            
            if result.returncode == 0:
                # Find the newly created person file
                person_files = [f for f in os.listdir(self.logs_dir) if f.startswith("person_")]
                if person_files:
                    latest_person_file = max(
                        [os.path.join(self.logs_dir, f) for f in person_files],
                        key=os.path.getmtime
                    )
                    print(f"✅ LinkedIn scraping completed: {os.path.basename(latest_person_file)}")
                    return latest_person_file
                else:
                    print("❌ LinkedIn scraping completed but no output file found")
                    return None
            else:
                print(f"❌ LinkedIn scraping failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ LinkedIn scraping timed out")
            return None
        except Exception as e:
            print(f"❌ LinkedIn scraping error: {e}")
            return None
    
    async def _create_temp_linkedin_scraper(self, original_scraper_path: str, linkedin_url: str) -> str:
        """Create a temporary version of the LinkedIn scraper with the specified URL."""
        with open(original_scraper_path, 'r') as f:
            content = f.read()
        
        # Replace the hardcoded URL with the provided one
        content = content.replace(
            'person = Person("https://www.linkedin.com/in/anshsingh200516/", driver=driver)',
            f'person = Person("{linkedin_url}", driver=driver)'
        )
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name
    
    async def parse_resume_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Run the existing resume parser for a given PDF.
        
        Args:
            pdf_path: Path to the resume PDF file
            
        Returns:
            Path to the generated JSON file, or None if failed
        """
        print(f"📄 Parsing resume PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"❌ Resume PDF not found: {pdf_path}")
            return None
        
        try:
            resume_parser_dir = os.path.join(self.project_root, "resume_parser")
            parse_script = os.path.join(resume_parser_dir, "parse_resume.ts")
            
            if not os.path.exists(parse_script):
                print(f"❌ Resume parser script not found: {parse_script}")
                return None
            
            # Run the TypeScript resume parser
            result = subprocess.run(
                ["npx", "tsx", parse_script, pdf_path],
                cwd=resume_parser_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                # Find the newly created resume file
                resume_files = [f for f in os.listdir(self.logs_dir) if f.startswith("resume_")]
                if resume_files:
                    latest_resume_file = max(
                        [os.path.join(self.logs_dir, f) for f in resume_files],
                        key=os.path.getmtime
                    )
                    print(f"✅ Resume parsing completed: {os.path.basename(latest_resume_file)}")
                    return latest_resume_file
                else:
                    print("❌ Resume parsing completed but no output file found")
                    return None
            else:
                print(f"❌ Resume parsing failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Resume parsing timed out")
            return None
        except Exception as e:
            print(f"❌ Resume parsing error: {e}")
            return None
    
    async def scrape_and_load_candidate_data(
        self, 
        knowledge_db: KnowledgeDatabase,
        linkedin_url: Optional[str] = None,
        resume_pdf_path: Optional[str] = None,
        linkedin_email: Optional[str] = None,
        linkedin_password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: scrape data and load into knowledge base.
        
        Args:
            knowledge_db: The knowledge database to load data into
            linkedin_url: LinkedIn profile URL to scrape
            resume_pdf_path: Path to resume PDF to parse
            linkedin_email: LinkedIn login email
            linkedin_password: LinkedIn login password
            
        Returns:
            Dictionary with results of the scraping and loading process
        """
        results = {
            "linkedin_file": None,
            "resume_file": None,
            "entries_before": len(knowledge_db.entries),
            "entries_after": 0,
            "success": False
        }
        
        print("🚀 Starting complete candidate data collection...")
        
        # Scrape LinkedIn if URL provided
        if linkedin_url and linkedin_email and linkedin_password:
            linkedin_file = await self.scrape_linkedin_profile(linkedin_url, linkedin_email, linkedin_password)
            results["linkedin_file"] = linkedin_file
        else:
            print("⚠️  LinkedIn scraping skipped (missing URL or credentials)")
        
        # Parse resume if PDF provided
        if resume_pdf_path:
            resume_file = await self.parse_resume_pdf(resume_pdf_path)
            results["resume_file"] = resume_file
        else:
            print("⚠️  Resume parsing skipped (no PDF provided)")
        
        # Load any existing data files if no new scraping was done
        if not results["linkedin_file"] and not results["resume_file"]:
            print("📂 Loading existing candidate data files...")
            loaded_files = knowledge_db.auto_load_latest_candidate_data(self.project_root)
            results["linkedin_file"] = loaded_files.get("linkedin")
            results["resume_file"] = loaded_files.get("resume")
        else:
            # Load the newly scraped files
            if results["linkedin_file"]:
                knowledge_db._parse_linkedin_data(results["linkedin_file"])
            if results["resume_file"]:
                knowledge_db._parse_resume_data(results["resume_file"])
        
        results["entries_after"] = len(knowledge_db.entries)
        results["success"] = results["entries_after"] > results["entries_before"]
        
        entries_added = results["entries_after"] - results["entries_before"]
        print(f"✅ Data collection completed. Added {entries_added} entries to knowledge base.")
        
        return results


# Convenience functions for direct use
async def scrape_linkedin_and_load(
    knowledge_db: KnowledgeDatabase,
    project_root: str,
    linkedin_url: str,
    email: str,
    password: str
) -> Optional[str]:
    """Convenience function to scrape LinkedIn and load into knowledge base."""
    integration = ScraperIntegration(project_root)
    linkedin_file = await integration.scrape_linkedin_profile(linkedin_url, email, password)
    if linkedin_file:
        knowledge_db._parse_linkedin_data(linkedin_file)
    return linkedin_file


async def parse_resume_and_load(
    knowledge_db: KnowledgeDatabase,
    project_root: str,
    pdf_path: str
) -> Optional[str]:
    """Convenience function to parse resume and load into knowledge base."""
    integration = ScraperIntegration(project_root)
    resume_file = await integration.parse_resume_pdf(pdf_path)
    if resume_file:
        knowledge_db._parse_resume_data(resume_file)
    return resume_file
