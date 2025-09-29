#!/usr/bin/env python3
"""
Unified Candidate Data Scraper

This script runs both the LinkedIn scraper and resume parser, then combines
their output into a single JSON file stored in the lda_logs folder.

Usage:
    python unified_scraper.py --linkedin-url "https://linkedin.com/in/username" --resume-pdf "path/to/resume.pdf"
    python unified_scraper.py --linkedin-url "https://linkedin.com/in/username"  # LinkedIn only
    python unified_scraper.py --resume-pdf "path/to/resume.pdf"  # Resume only
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class UnifiedScraper:
    """Unified scraper that combines LinkedIn and resume data into a single JSON file."""
    
    def __init__(self):
        """Initialize the unified scraper."""
        # Get the directory paths
        self.lda_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(self.lda_dir))
        self.lda_logs_dir = os.path.join(self.lda_dir, "lda_logs")
        self.main_logs_dir = os.path.join(self.project_root, "logs")
        
        # Create lda_logs directory if it doesn't exist
        os.makedirs(self.lda_logs_dir, exist_ok=True)
        os.makedirs(self.main_logs_dir, exist_ok=True)
        
        print(f"📁 LDA directory: {self.lda_dir}")
        print(f"📁 Project root: {self.project_root}")
        print(f"📁 LDA logs directory: {self.lda_logs_dir}")
    
    def run_linkedin_scraper(self, linkedin_url: str, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Run the LinkedIn scraper and return the parsed data.
        
        Args:
            linkedin_url: LinkedIn profile URL to scrape
            email: LinkedIn login email
            password: LinkedIn login password
            
        Returns:
            Parsed LinkedIn data or None if failed
        """
        print(f"🔍 Scraping LinkedIn profile: {linkedin_url}")
        
        try:
            # Call the LinkedIn scraper directly with the URL parameter
            scraper_path = os.path.join(self.project_root, "linkdin_scrapper.py")
            
            if not os.path.exists(scraper_path):
                print(f"❌ LinkedIn scraper not found: {scraper_path}")
                return None
            
            # Set environment variables
            env = os.environ.copy()
            env["LINKEDIN_EMAIL"] = email
            env["LINKEDIN_PASSW"] = password
            
            # Run the scraper directly with URL parameter
            result = subprocess.run(
                [sys.executable, scraper_path, "--url", linkedin_url],
                env=env,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Find the newly created person file
                person_files = [f for f in os.listdir(self.main_logs_dir) if f.startswith("person_")]
                if person_files:
                    latest_person_file = max(
                        [os.path.join(self.main_logs_dir, f) for f in person_files],
                        key=os.path.getmtime
                    )
                    
                    # Load the LinkedIn data
                    with open(latest_person_file, 'r') as f:
                        linkedin_data = json.load(f)
                    
                    print(f"✅ LinkedIn scraping completed: {os.path.basename(latest_person_file)}")
                    return linkedin_data
                else:
                    print("❌ LinkedIn scraping completed but no output file found")
                    print(f"📄 Scraper stdout: {result.stdout[:500]}")
                    print(f"📄 Scraper stderr: {result.stderr[:500]}")
                    return None
            else:
                print(f"❌ LinkedIn scraping failed: {result.stderr}")
                print(f"📄 Scraper stdout: {result.stdout[:500]}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ LinkedIn scraping timed out")
            return None
        except Exception as e:
            print(f"❌ LinkedIn scraping error: {e}")
            return None
    
    def run_resume_parser(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Run the resume parser and return the parsed data.
        
        Args:
            pdf_path: Path to the resume PDF file
            
        Returns:
            Parsed resume data or None if failed
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
            
            # Check if node_modules exist, if not install dependencies
            node_modules_dir = os.path.join(resume_parser_dir, "node_modules")
            if not os.path.exists(node_modules_dir):
                print("📦 Installing resume parser dependencies...")
                install_result = subprocess.run(
                    ["npm", "install"],
                    cwd=resume_parser_dir,
                    capture_output=True,
                    text=True,
                    timeout=180  # 3 minute timeout for npm install
                )
                
                if install_result.returncode != 0:
                    print(f"❌ Failed to install dependencies: {install_result.stderr}")
                    return None
                print("✅ Dependencies installed successfully")
            
            # Try multiple execution methods
            execution_methods = [
                (["npx", "tsx", parse_script, pdf_path], "tsx"),
                (["npx", "ts-node", parse_script, pdf_path], "ts-node"),
                (["node", "--loader", "ts-node/esm", parse_script, pdf_path], "ts-node/esm")
            ]
            
            for command, method in execution_methods:
                print(f"🔍 Trying resume parser with {method}...")
                try:
                    result = subprocess.run(
                        command,
                        cwd=resume_parser_dir,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Resume parser executed successfully with {method}")
                        break
                    else:
                        print(f"⚠️ {method} failed: {result.stderr[:200]}...")
                        continue
                        
                except subprocess.TimeoutExpired:
                    print(f"⚠️ {method} timed out")
                    continue
                except Exception as e:
                    print(f"⚠️ {method} error: {e}")
                    continue
            else:
                print("❌ All resume parser execution methods failed")
                return None
            
            # Find the newly created resume file
            resume_files = [f for f in os.listdir(self.main_logs_dir) if f.startswith("resume_")]
            if resume_files:
                latest_resume_file = max(
                    [os.path.join(self.main_logs_dir, f) for f in resume_files],
                    key=os.path.getmtime
                )
                
                # Load the resume data
                with open(latest_resume_file, 'r') as f:
                    resume_data = json.load(f)
                
                print(f"✅ Resume parsing completed: {os.path.basename(latest_resume_file)}")
                return resume_data
            else:
                print("❌ Resume parsing completed but no output file found")
                print(f"📄 Parser stdout: {result.stdout[:500]}")
                print(f"📄 Parser stderr: {result.stderr[:500]}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Resume parsing timed out after 5 minutes")
            return None
        except Exception as e:
            print(f"❌ Resume parsing error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def combine_and_save_data(self, linkedin_data: Optional[Dict[str, Any]], 
                             resume_data: Optional[Dict[str, Any]], 
                             candidate_name: Optional[str] = None) -> str:
        """
        Combine LinkedIn and resume data into a single JSON file and save to lda_logs.
        
        Args:
            linkedin_data: LinkedIn scraping results
            resume_data: Resume parsing results
            candidate_name: Optional candidate name for filename
            
        Returns:
            Path to the saved combined JSON file
        """
        print("🔄 Combining and saving data...")
        
        # Create combined data structure
        combined_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "candidate_name": candidate_name,
            "data_sources": {
                "linkedin": linkedin_data is not None,
                "resume": resume_data is not None
            },
            "linkedin_data": linkedin_data,
            "resume_data": resume_data,
            "metadata": {
                "scraper_version": "unified_scraper_v1.0.0",
                "linkedin_entries": 0,
                "resume_entries": 0,
                "total_entries": 0
            }
        }
        
        # Extract candidate name if not provided
        if not candidate_name:
            if linkedin_data and linkedin_data.get('name'):
                candidate_name = linkedin_data['name']
            elif resume_data and resume_data.get('sections', {}).get('HEADER'):
                header_data = resume_data['sections']['HEADER']
                candidate_name = header_data[0] if header_data else "Unknown"
            else:
                candidate_name = "Unknown"
        
        combined_data["candidate_name"] = candidate_name
        
        # Count entries for metadata
        if linkedin_data:
            linkedin_entries = (
                len(linkedin_data.get('experiences', [])) +
                len(linkedin_data.get('educations', [])) +
                len(linkedin_data.get('skills', [])) +
                len(linkedin_data.get('projects', [])) +
                len(linkedin_data.get('licenses', [])) +
                len(linkedin_data.get('honors', [])) +
                (1 if linkedin_data.get('name') else 0) +
                (1 if linkedin_data.get('about') else 0)
            )
            combined_data["metadata"]["linkedin_entries"] = linkedin_entries
        
        if resume_data:
            resume_entries = sum(len(section) for section in resume_data.get('sections', {}).values())
            combined_data["metadata"]["resume_entries"] = resume_entries
        
        combined_data["metadata"]["total_entries"] = (
            combined_data["metadata"]["linkedin_entries"] + 
            combined_data["metadata"]["resume_entries"]
        )
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = candidate_name.replace(" ", "_").replace(".", "_") if candidate_name else "unknown"
        filename = f"combined_candidate_data_{safe_name}_{timestamp}.json"
        
        # Save to lda_logs directory
        filepath = os.path.join(self.lda_logs_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Combined data saved to: {filepath}")
        return filepath
    
    async def run_unified_scraping(self, linkedin_url: Optional[str] = None,
                                 resume_pdf_path: Optional[str] = None,
                                 linkedin_email: Optional[str] = None,
                                 linkedin_password: Optional[str] = None,
                                 candidate_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete unified scraping workflow.
        
        Args:
            linkedin_url: LinkedIn profile URL to scrape
            resume_pdf_path: Path to resume PDF to parse
            linkedin_email: LinkedIn login email
            linkedin_password: LinkedIn login password
            candidate_name: Optional candidate name
            
        Returns:
            Results dictionary with file paths and statistics
        """
        results = {
            "linkedin_data": None,
            "resume_data": None,
            "combined_file": None,
            "success": False,
            "errors": []
        }
        
        print("🚀 Starting unified candidate data scraping...")
        print("=" * 60)
        
        # Track individual operation success
        linkedin_attempted = False
        resume_attempted = False
        
        # Scrape LinkedIn if URL provided
        if linkedin_url and linkedin_email and linkedin_password:
            linkedin_attempted = True
            print("🔍 Attempting LinkedIn scraping...")
            try:
                linkedin_data = self.run_linkedin_scraper(linkedin_url, linkedin_email, linkedin_password)
                results["linkedin_data"] = linkedin_data
                if not linkedin_data:
                    results["errors"].append("LinkedIn scraping failed")
                    print("⚠️  LinkedIn scraping failed, continuing with resume parsing...")
                else:
                    print("✅ LinkedIn scraping successful, continuing with resume parsing...")
            except Exception as e:
                results["errors"].append(f"LinkedIn scraping error: {str(e)}")
                print(f"⚠️  LinkedIn scraping error: {e}, continuing with resume parsing...")
        elif linkedin_url:
            results["errors"].append("LinkedIn URL provided but missing email/password")
            print("⚠️  LinkedIn scraping skipped (missing credentials)")
        else:
            print("⚠️  LinkedIn scraping skipped (no URL provided)")
        
        # Parse resume if PDF provided
        if resume_pdf_path:
            resume_attempted = True
            print("📄 Attempting resume parsing...")
            try:
                resume_data = self.run_resume_parser(resume_pdf_path)
                results["resume_data"] = resume_data
                if not resume_data:
                    results["errors"].append("Resume parsing failed")
                    print("⚠️  Resume parsing failed")
                else:
                    print("✅ Resume parsing successful")
            except Exception as e:
                results["errors"].append(f"Resume parsing error: {str(e)}")
                print(f"⚠️  Resume parsing error: {e}")
        else:
            print("⚠️  Resume parsing skipped (no PDF provided)")
        
        # Determine overall success based on what was attempted and succeeded
        linkedin_success = results["linkedin_data"] is not None
        resume_success = results["resume_data"] is not None
        
        # Success if at least one operation succeeded OR if partial data was collected
        partial_success = (linkedin_attempted and linkedin_success) or (resume_attempted and resume_success)
        
        # Combine and save data if we have at least one source
        if results["linkedin_data"] or results["resume_data"]:
            try:
                combined_file = self.combine_and_save_data(
                    results["linkedin_data"], 
                    results["resume_data"],
                    candidate_name
                )
                results["combined_file"] = combined_file
                results["success"] = True
                print("✅ Successfully combined and saved data from available sources")
            except Exception as e:
                results["errors"].append(f"Failed to combine data: {str(e)}")
                print(f"❌ Failed to combine data: {e}")
        else:
            if linkedin_attempted or resume_attempted:
                results["errors"].append("No data collected from either source")
            else:
                results["errors"].append("No scraping operations were attempted")
        
        # Print detailed summary
        print("\n" + "=" * 60)
        print("📊 Scraping Results Summary:")
        print(f"   LinkedIn data: {'✅' if results['linkedin_data'] else '❌'}")
        print(f"   Resume data: {'✅' if results['resume_data'] else '❌'}")
        print(f"   Combined file: {os.path.basename(results['combined_file']) if results['combined_file'] else 'None'}")
        print(f"   Success: {'✅' if results['success'] else '❌'}")
        
        if results["errors"]:
            print(f"   Errors: {', '.join(results['errors'])}")
        
        # Show what data was collected
        if results["linkedin_data"]:
            linkedin_summary = self._get_linkedin_summary(results["linkedin_data"])
            print(f"   LinkedIn: {linkedin_summary}")
        
        if results["resume_data"]:
            resume_summary = self._get_resume_summary(results["resume_data"])
            print(f"   Resume: {resume_summary}")
        
        if results["combined_file"]:
            print(f"\n💾 Combined data saved to:")
            print(f"   {results['combined_file']}")
        
        # Provide next steps or troubleshooting info
        if not results["success"]:
            print(f"\n🔧 Troubleshooting:")
            if not results["linkedin_data"] and linkedin_url:
                print(f"   - Check LinkedIn credentials in environment variables")
                print(f"   - Verify LinkedIn URL is accessible")
            if not results["resume_data"] and resume_pdf_path:
                print(f"   - Check if PDF file is valid and readable")
                print(f"   - Ensure Node.js and npm are installed")
        
        return results
    
    def _get_linkedin_summary(self, linkedin_data: Dict[str, Any]) -> str:
        """Generate a summary of LinkedIn data."""
        name = linkedin_data.get('name', 'Unknown')
        exp_count = len(linkedin_data.get('experiences', []))
        edu_count = len(linkedin_data.get('educations', []))
        skills_count = len(linkedin_data.get('skills', []))
        return f"{name} ({exp_count} exp, {edu_count} edu, {skills_count} skills)"
    
    def _get_resume_summary(self, resume_data: Dict[str, Any]) -> str:
        """Generate a summary of resume data."""
        sections = resume_data.get('sections', {})
        section_count = len(sections)
        total_items = sum(len(items) for items in sections.values())
        return f"{section_count} sections, {total_items} items"


async def main():
    """Main entry point for the unified scraper."""
    parser = argparse.ArgumentParser(
        description="Unified candidate data scraper (LinkedIn + Resume)"
    )
    
    parser.add_argument(
        "--linkedin-url",
        type=str,
        help="LinkedIn profile URL to scrape"
    )
    
    parser.add_argument(
        "--resume-pdf",
        type=str,
        help="Path to resume PDF file to parse"
    )
    
    parser.add_argument(
        "--candidate-name",
        type=str,
        help="Candidate name (for filename generation)"
    )
    
    parser.add_argument(
        "--linkedin-email",
        type=str,
        default=os.getenv("LINKEDIN_EMAIL"),
        help="LinkedIn login email (can also be set via LINKEDIN_EMAIL env var)"
    )
    
    parser.add_argument(
        "--linkedin-password",
        type=str,
        default=os.getenv("LINKEDIN_PASSW"),
        help="LinkedIn login password (can also be set via LINKEDIN_PASSW env var)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.linkedin_url and not args.resume_pdf:
        print("❌ Error: Must provide either --linkedin-url or --resume-pdf (or both)")
        parser.print_help()
        sys.exit(1)
    
    if args.linkedin_url and (not args.linkedin_email or not args.linkedin_password):
        print("❌ Error: LinkedIn scraping requires email and password")
        print("   Set LINKEDIN_EMAIL and LINKEDIN_PASSW environment variables")
        print("   or use --linkedin-email and --linkedin-password arguments")
        sys.exit(1)
    
    # Initialize scraper
    scraper = UnifiedScraper()
    
    try:
        # Run unified scraping
        results = await scraper.run_unified_scraping(
            linkedin_url=args.linkedin_url,
            resume_pdf_path=args.resume_pdf,
            linkedin_email=args.linkedin_email,
            linkedin_password=args.linkedin_password,
            candidate_name=args.candidate_name
        )
        
        if results["success"]:
            print("\n🎉 Unified scraping completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Unified scraping failed!")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
