# Unified Scraper Usage Guide

## 🎯 Overview

The `unified_scraper.py` is a single file that:
1. Runs your existing `linkdin_scrapper.py` 
2. Runs your existing `resume_parser/parse_resume.ts`
3. Combines the results into a single JSON file
4. Stores it in the `lda_logs/` folder inside the `lda` directory

## 📁 File Structure

```
Brain/lda/
├── unified_scraper.py          # Single file that does everything
├── lda_logs/                   # Combined data storage
│   └── combined_candidate_data_Name_TIMESTAMP.json
├── knowledge_db.py             # Enhanced to load combined data
└── main.py                     # Updated to use combined data
```

## 🚀 Usage Examples

### LinkedIn + Resume (Complete)
```bash
cd Brain/lda
export LINKEDIN_EMAIL="your_email@example.com"
export LINKEDIN_PASSW="your_password"

python unified_scraper.py \
  --linkedin-url "https://linkedin.com/in/username" \
  --resume-pdf "../../path/to/resume.pdf"
```

### LinkedIn Only
```bash
cd Brain/lda
python unified_scraper.py \
  --linkedin-url "https://linkedin.com/in/username" \
  --linkedin-email "email@example.com" \
  --linkedin-password "password"
```

### Resume Only
```bash
cd Brain/lda
python unified_scraper.py --resume-pdf "../../path/to/resume.pdf"
```

### With Custom Candidate Name
```bash
cd Brain/lda
python unified_scraper.py \
  --linkedin-url "https://linkedin.com/in/johndoe" \
  --candidate-name "John Doe"
```

## 📊 Output Format

The unified scraper creates a combined JSON file:

```json
{
  "timestamp": "2025-01-27T10:30:00",
  "candidate_name": "Vatsal Jain",
  "data_sources": {
    "linkedin": true,
    "resume": true
  },
  "linkedin_data": {
    "name": "Vatsal Jain",
    "about": "...",
    "experiences": [...],
    "educations": [...],
    "skills": [...],
    "projects": [...],
    "licenses": [...],
    "honors": [...]
  },
  "resume_data": {
    "sections": {
      "HEADER": ["VATSAL JAIN"],
      "IIT COURSE": [...],
      "INTERNSHIPS": [...],
      "PROJECTS": [...],
      "TECHNICAL SKILLS": [...]
    }
  },
  "metadata": {
    "scraper_version": "unified_scraper_v1.0.0",
    "linkedin_entries": 60,
    "resume_entries": 83,
    "total_entries": 143
  }
}
```

## 🔧 Integration with Interview System

The interview system automatically uses the combined data:

1. **Run unified scraper** to collect fresh data:
   ```bash
   cd Brain/lda
   python unified_scraper.py --linkedin-url "https://linkedin.com/in/candidate"
   ```

2. **Run interview system** - it automatically loads the latest combined data:
   ```bash
   cd Brain/lda
   python main.py
   ```

## 📋 What Gets Extracted

### LinkedIn Data
- ✅ Personal info (name, about)
- ✅ Work experiences (5+ positions)
- ✅ Key achievements (15+ accomplishments)
- ✅ Education (degrees, GPAs)
- ✅ Skills (20+ technical skills)
- ✅ Projects (9+ projects)
- ✅ Certifications (3+ certs)
- ✅ Honors and awards

### Resume Data
- ✅ Personal info (name)
- ✅ Education (degrees, institutions, GPAs)
- ✅ Internships and positions
- ✅ Technical skills (60+ skills)
- ✅ Projects (8+ projects)
- ✅ Academic achievements
- ✅ Course details

### Total: 143+ knowledge entries!

## 🔄 How It Works

1. **LinkedIn Scraping**: 
   - Modifies your existing `linkdin_scrapper.py` to use the provided URL
   - Runs Selenium automation
   - Saves to `logs/person_*.json`

2. **Resume Parsing**:
   - Runs your existing `resume_parser/parse_resume.ts`
   - Processes PDF with TypeScript
   - Saves to `logs/resume_*.json`

3. **Data Combination**:
   - Loads both JSON files
   - Combines into unified format
   - Saves to `lda_logs/combined_candidate_data_*.json`

4. **Knowledge Base Integration**:
   - Interview system auto-loads from `lda_logs/`
   - Extracts 143+ entries for comprehensive fact-checking
   - Enables accurate lie detection and informed questioning

## 🎉 Benefits

- ✅ **Single command** runs both scrapers
- ✅ **Combined output** in one JSON file
- ✅ **Organized storage** in dedicated `lda_logs/` folder
- ✅ **Automatic integration** with interview system
- ✅ **Comprehensive data** extraction (143+ entries vs 1-2 before)
- ✅ **Uses existing tools** - no rewriting needed
- ✅ **Backwards compatible** - still works with old separate files

## ⚡ Quick Start

```bash
# 1. Set LinkedIn credentials
export LINKEDIN_EMAIL="your_email@example.com"
export LINKEDIN_PASSW="your_password"

# 2. Run unified scraper
cd Brain/lda
python unified_scraper.py \
  --linkedin-url "https://linkedin.com/in/candidate" \
  --resume-pdf "../../candidate_resume.pdf"

# 3. Run interview (automatically uses combined data)
python main.py
```

The interview system will now have comprehensive candidate information for accurate lie detection and informed questioning! 🎯
