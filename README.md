# LinkedIn Profile Scraper & Resume Parser


## 📋 Requirements

### System Requirements
- **Node.js**: Version 16.0.0 or higher
- **Python**: Version 3.7 or higher
- **Chrome Browser**: For LinkedIn scraping (via Selenium)
- **ChromeDriver**: Compatible with your Chrome version

### Operating System
- macOS (tested)
- Linux (should work)
- Windows (with appropriate path adjustments)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "eightfold finals"
```

### 2. Install Python Dependencies
```bash
# Install the LinkedIn scraper dependencies
pip3 install selenium requests lxml python-dotenv

# Or install from requirements file
cd linkedin_scraper
pip3 install -r requirements.txt
cd ..
```

### 3. Install Node.js Dependencies
```bash
cd resume_parser
npm install
cd ..
```

### 4. Setup ChromeDriver
```bash
# Download ChromeDriver from https://chromedriver.chromium.org/
# Make sure it matches your Chrome version
# Set the environment variable (add to your ~/.bashrc or ~/.zshrc)
export CHROMEDRIVER=/path/to/your/chromedriver
```

### 5. Configure LinkedIn Credentials
Create a `.env` file in the project root:
```bash
# .env file
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSW=your-linkedin-password
```

## 📖 Usage

### Quick Start (Automated)
The easiest way to run both LinkedIn scraping and resume parsing:

```bash
# Make sure the script is executable
chmod +x run.sh

# Run with default configured values
./run.sh
```

**Note**: Edit the `run.sh` file to configure:
- `LINKEDIN_URL`: The LinkedIn profile URL to scrape
- `RESUME_PATH`: Path to the PDF resume file

### Manual Usage

#### LinkedIn Profile Scraping
```bash
# Edit linkdin_scrapper.py to set the LinkedIn URL
python3 linkdin_scrapper.py
```

#### Resume Parsing
```bash
cd resume_parser

# Parse a specific resume
npm run dev parse_resume.ts /path/to/resume.pdf

# Or use the compiled version
npm run build
npm run parse /path/to/resume.pdf

# View extracted sections from parsed data
npx ts-node view_sections.ts ../logs/resume_filename.json
```

## 📁 Project Structure

```
eightfold finals/
├── README.md                          # This file
├── run.sh                            # Main automation script
├── linkdin_scrapper.py               # LinkedIn scraper script
├── .env                              # Environment variables (create this)
├── 1757659381503.pdf                 # Example resume file
├── linkedin_scraper/                 # LinkedIn scraping library
│   ├── linkedin_scraper/             # Core scraper modules
│   ├── requirements.txt              # Python dependencies
│   └── README.md                     # Library documentation
├── resume_parser/                    # Resume parsing module
│   ├── parse_resume.ts              # Main parser implementation
│   ├── view_sections.ts             # Section viewer utility
│   ├── example_usage.ts             # Usage examples
│   ├── package.json                 # Node.js dependencies
│   ├── tsconfig.json                # TypeScript configuration
│   ├── open-resume/                 # Open-resume library integration
│   └── README.md                    # Parser documentation
└── logs/                            # Output directory
    ├── person_*.json                # LinkedIn profile data
    └── resume_*.json                # Parsed resume data
```

## 📊 Output Format

### LinkedIn Profile Data (`logs/person_*.json`)
```json
{
  "linkedin_url": "https://www.linkedin.com/in/username/",
  "name": "Full Name",
  "about": "Professional summary...",
  "experiences": [
    {
      "institution_name": "Company Name",
      "position_title": "Job Title",
      "from_date": "Start Date",
      "to_date": "End Date",
      "description": "Job description...",
      "location": "Location"
    }
  ],
  "educations": [...],
  "skills": [...],
  "projects": [...],
  "scraped_at": "2025-09-23T07:04:56.123Z"
}
```

### Resume Data (`logs/resume_*.json`)
```json
{
  "timestamp": "2025-09-23T01:34:57.663Z",
  "filename": "resume.pdf",
  "sections": {
    "ACADEMIC DETAILS": ["B.Tech in Engineering", "University Name", "CGPA: 8.5"],
    "TECHNICAL SKILLS": ["Python", "JavaScript", "Machine Learning"],
    "PROJECTS": ["Project descriptions..."],
    "INTERNSHIPS": ["Work experience details..."]
  },
  "metadata": {
    "parserVersion": "custom-parser-v1.0.0",
    "processingTime": 1250,
    "status": "success"
  }
}
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required for LinkedIn scraping
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSW=your_password

# Optional: ChromeDriver path
CHROMEDRIVER=/usr/local/bin/chromedriver
```

### Script Configuration (run.sh)
Edit the following variables in `run.sh`:
```bash
# LinkedIn profile to scrape
LINKEDIN_URL="https://www.linkedin.com/in/your-profile/"

# Resume file to parse
RESUME_PATH="/path/to/your/resume.pdf"
```

## 🔧 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   ```bash
   # Download ChromeDriver and set the path
   export CHROMEDRIVER=/path/to/chromedriver
   ```

2. **LinkedIn login issues**
   - Check your credentials in the `.env` file
   - Ensure your LinkedIn account is not locked
   - Consider using a dedicated LinkedIn account for scraping

3. **Resume parsing errors**
   - Ensure the file is a valid PDF
   - Check file permissions
   - Try with a simpler resume format

4. **Node.js version issues**
   ```bash
   # Check Node.js version
   node --version
   # Should be 16.0.0 or higher
   ```

5. **Python dependency issues**
   ```bash
   # Install missing packages
   pip3 install selenium requests lxml python-dotenv
   ```

### Permission Issues
```bash
# Make scripts executable
chmod +x run.sh
```

## 📝 Examples

### Example LinkedIn URL Formats
```
https://www.linkedin.com/in/firstname-lastname/
https://www.linkedin.com/in/username/
```

### Example Resume Processing
```bash
# Process a resume and view results
./run.sh

# Check the logs directory for output
ls -la logs/
```

**Last Updated**: September 23, 2025
