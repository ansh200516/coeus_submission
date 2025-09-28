import sys
import os
import json
import datetime
from dataclasses import asdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "linkedin_scraper"))

from linkedin_scraper import Person, actions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()


def person_to_dict(person):
    """Convert Person object to dictionary for JSON serialization"""
    person_dict = {
        "linkedin_url": person.linkedin_url,
        "name": person.name,
        "about": person.about,
        "experiences": [asdict(exp) for exp in person.experiences],
        "educations": [asdict(edu) for edu in person.educations],
        "licenses": [asdict(lic) for lic in person.licenses],
        "projects": [asdict(proj) for proj in person.projects],
        "skills": [asdict(skill) for skill in person.skills],
        "courses": [asdict(course) for course in person.courses],
        "honors": [asdict(honor) for honor in person.honors],
        "interests": [asdict(interest) for interest in person.interests],
        "accomplishments": [asdict(acc) for acc in person.accomplishments],
        "contacts": [asdict(contact) for contact in person.contacts],
        "scraped_at": datetime.datetime.now().isoformat(),
    }
    return person_dict


def save_person_to_log(person, filename=None):
    """Save Person object as JSON to logs folder"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = (
            person.name.replace(" ", "_").replace(".", "_")
            if person.name
            else "unknown"
        )
        filename = f"person_{safe_name}_{timestamp}.json"

    # Convert person to dict and save as JSON
    person_dict = person_to_dict(person)
    filepath = os.path.join(logs_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(person_dict, f, indent=2, ensure_ascii=False)

    print(f"Person data saved to: {filepath}")
    return filepath


if __name__ == "__main__":
    # Main execution
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Profile Scraper')
    parser.add_argument('--url', type=str, default="https://www.linkedin.com/in/anshsingh200516/",
                        help='LinkedIn profile URL to scrape')
    args = parser.parse_args()
    
    linkedin_url = args.url
    
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSW")
    if not email or not password:
        print(
            "Error: LINKEDIN_EMAIL and LINKEDIN_PASSW environment variables must be set"
        )
        sys.exit(1)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"🔐 Attempting to login to LinkedIn...")
        actions.login(driver, email, password)
        print(f"✅ LinkedIn login successful")
        
        person = Person(linkedin_url, driver=driver)

        # Print the person object (as before)
        print(person)

        # Save person data to JSON log file
        log_filepath = save_person_to_log(person)
        print(f"✅ LinkedIn scraping completed successfully")

    except Exception as e:
        print(f"❌ LinkedIn scraping failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Close the driver
        if driver:
            driver.quit()
