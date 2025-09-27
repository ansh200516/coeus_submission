# Resume Parser

A TypeScript-based resume parser that uses the open-resume library to extract structured data from PDF resumes and save the results as JSON files in the logs directory.

## Features

- 📄 **PDF Resume Parsing**: Extracts structured data from PDF resumes with intelligent section detection
- 🔍 **Section-Based Extraction**: Automatically identifies and parses distinct resume sections like:
  - ACADEMIC DETAILS
  - SCHOLASTIC ACHIEVEMENTS
  - INTERNSHIPS
  - PROJECTS
  - TECHNICAL SKILLS
  - COURSES DONE
  - QUALIFYING EXAM
  - POSITIONS OF RESPONSIBILITY
- 💾 **Complete JSON Output**: Saves all parsed data including raw sections and structured data
- 📊 **Section Viewer**: Includes a dedicated tool to view all extracted sections
- 📝 **Detailed Logging**: Provides comprehensive parsing summaries and error handling
- ⚡ **TypeScript Support**: Fully typed with modern TypeScript features

## Installation

1. **Install Dependencies**:
   ```bash
   cd resume_parser
   npm install
   ```

2. **Build the Project** (optional):
   ```bash
   npm run build
   ```

## Usage

### Method 1: Direct TypeScript Execution
```bash
# Parse a specific resume
npm run dev parse_resume.ts /path/to/your/resume.pdf

# Run the example with the provided resume
npm run dev example_usage.ts
```

### Method 2: Compiled JavaScript
```bash
# Build first
npm run build

# Then run
node dist/parse_resume.js /path/to/your/resume.pdf
```

### Method 3: Using npm script
```bash
# After building
npm run parse /path/to/your/resume.pdf
```

### Method 4: View Extracted Sections
```bash
# View sections from the latest parsed resume
npx ts-node view_sections.ts

# View sections from a specific JSON file
npx ts-node view_sections.ts ../logs/resume_example.json
```

## Example Usage

The project includes an example script that demonstrates parsing the provided resume:

```bash
npm run dev example_usage.ts
```

This will:
1. Parse the `2023CE11156_it.pdf` file in the parent directory
2. Extract structured data including:
   - Personal profile (name, email, phone, location, URL)
   - Work experiences
   - Education details
   - Projects
   - Skills
3. Save the results as a JSON file in the `../logs/` directory
4. Display a comprehensive parsing summary

## Output Format

The parser generates JSON files with the following structure:

```json
{
  "timestamp": "2025-09-23T12:34:56.789Z",
  "filename": "resume.pdf",
  "parsedData": {
    "profile": {
      "name": "Ansh Singh",
      "email": "ansh@example.com",
      "phone": "+91-9876543210",
      "location": "Indian Institute of Technology Delhi",
      "url": "https://linkedin.com/in/ansh",
      "summary": "Computer Science student..."
    },
    "workExperiences": [
      {
        "company": "CLAN Lab, Aarhus University Denmark",
        "jobTitle": "Research Intern",
        "date": "May'25 - July'25",
        "descriptions": ["Memory-augmentation for Cost-Effective..."]
      }
    ],
    "educations": [...],
    "projects": [...],
    "skills": {...},
    "custom": {
      "descriptions": [],
      "sections": {
        "ACADEMIC DETAILS": ["B.Tech in Civil Engineering", "IIT Delhi", "CGPA: 7.6"],
        "SCHOLASTIC ACHIEVEMENTS": ["DDSA Scholar: 15,000 DKK", "KVPY Fellow 2021"],
        "INTERNSHIPS": ["CLAN Lab research details...", "Vision Lab MLOps work..."],
        "PROJECTS": ["Latent Adaptive Subspace Retrieval", "AlphaZero from Scratch"],
        "TECHNICAL SKILLS": ["OpenMP", "Docker", "Git", "Python", "C++"]
      }
    }
  },
  "metadata": {
    "parserVersion": "custom-parser-v1.0.0",
    "processingTime": 55,
    "status": "success"
  }
}
```

## File Structure

```
resume_parser/
├── parse_resume.ts          # Main parser implementation with section extraction
├── view_sections.ts         # Section viewer tool
├── example_usage.ts         # Usage example
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── README.md               # This file
└── open-resume/            # Open-resume library (submodule)
```

## Dependencies

- **pdfjs-dist**: PDF parsing capabilities
- **typescript**: TypeScript compiler
- **ts-node**: Direct TypeScript execution
- **@types/node**: Node.js type definitions

## Limitations

- Only works with single-column PDF resumes
- Optimized for English language resumes
- Requires readable, text-based PDFs (not scanned images)

## Error Handling

The parser includes comprehensive error handling for:
- Missing or invalid PDF files
- Parsing failures
- File system errors
- Invalid input formats

All errors are logged to the JSON output file with detailed error messages and metadata.

## Support

For issues or questions about the open-resume parsing algorithm, refer to the [open-resume documentation](https://github.com/xitanggg/open-resume).
