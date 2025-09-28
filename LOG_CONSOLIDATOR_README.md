# Interview Log Consolidator

This script consolidates log files from both interview systems into a single, comprehensive log file.

## Overview

The Log Consolidator processes log files from:

1. **LDA Interview System** (`Brain/lda/main.py`) - Generates `interview_summary_*.json` files
2. **Code Interview System** (`Brain/code interview agent/main.py`) - Generates `performance_*.json` files

## Features

The script extracts and consolidates the following data:

- ✅ **Summary**: Interview summary, strengths, areas for improvement, and hiring recommendation from LDA
- ✅ **Static Knowledge**: LinkedIn and resume data (all claims from knowledge base entries)
- ✅ **Job Description**: Job description data from knowledge base
- ✅ **Lies**: Detected lies during interviews with explanations and confidence scores
- ✅ **Candidate Scores**: Code interview performance scores and metrics
- ✅ **Hirability Score**: AI-powered analysis of candidate fit based on LinkedIn/resume vs job requirements

## Usage

### Basic Usage

```bash
# Run from the project root directory
python log_consolidator.py

# Or make it executable and run directly
chmod +x log_consolidator.py
./log_consolidator.py
```

### What the Script Does

1. **Auto-detects** the latest log files from both systems
2. **Extracts** relevant data from each log type
3. **Consolidates** all data into a single structured format
4. **Saves** the result to `consolidated_logs/consolidated_interview_log_TIMESTAMP.json`

### Output Structure

The consolidated log file contains:

```json
{
    "metadata": {
        "consolidation_timestamp": "2025-09-28T04:17:45.251969",
        "consolidator_version": "1.0.0",
        "sources": {
            "lda_interview": true,
            "code_interview": true
        }
    },
    "summary": {
        "overall_summary": "...",
        "strengths": [...],
        "areas_for_improvement": [...],
        "hiring_recommendation_from_lda": "..."
    },
    "static_knowledge": {
        "linkedin": [...],
        "resume": [...]
    },
    "job_description": [...],
    "lies": [...],
    "candidate_scores": {
        "candidate": {...},
        "problem": {...},
        "scores": {...},
        "time_performance": {...},
        "test_results": {...},
        "feedback": {...}
    },
    "hirability_score": {
        "overall_score": 75.5,
        "recommendation": "Hire",
        "category_breakdown": {...},
        "estimated_experience_years": 2.5,
        "scoring_methodology": {...}
    }
}
```

## Hirability Score Algorithm

The hirability score is calculated using a weighted scoring system that analyzes candidate data against job requirements:

### Scoring Categories (Weighted)

1. **Technical Skills (30%)**: Programming languages, frameworks, databases, cloud platforms
2. **AI/ML Experience (25%)**: Machine learning, deep learning, data science experience
3. **Experience Level (20%)**: Years of experience, seniority, leadership roles
4. **Education Background (15%)**: Degrees, certifications, academic achievements
5. **Soft Skills (10%)**: Communication, teamwork, problem-solving abilities

### Scoring Logic

- **Job-Relevant Skills**: 2 points (skills mentioned in both candidate profile and job description)
- **Additional Skills**: 1 point (skills in candidate profile but not specifically required)
- **Score Range**: 0-100 with weighted averages across categories

### Hiring Recommendations

- **80-100**: Strong Hire
- **65-79**: Hire  
- **50-64**: Weak Hire
- **35-49**: Weak No Hire
- **0-34**: No Hire

### Output Includes

- Overall weighted score
- Category-wise breakdown with matched skills
- Estimated years of experience
- Detailed analysis summary
- Scoring methodology transparency

## Requirements

- Python 3.7+
- Access to log files in:
  - `old logs/` directory (for LDA interview logs)
  - `Brain/code interview agent/interviews/` directory (for code interview logs)

## Log File Locations

### LDA Interview Logs
- **Location**: `old logs/interview_summary_*.json`
- **Contains**: Interview summaries, conversation history, knowledge base, detected lies

### Code Interview Logs
- **Location**: `Brain/code interview agent/interviews/performance_*.json`
- **Contains**: Candidate scores, problem details, test results, performance metrics

## Output

- **Directory**: `consolidated_logs/`
- **Filename**: `consolidated_interview_log_YYYYMMDD_HHMMSS.json`
- **Format**: Structured JSON with all extracted data

## Example Output Summary

```
📊 CONSOLIDATED LOG SUMMARY
============================================================
🕒 Consolidation Time: 2025-09-28T04:17:45.251969
📁 Sources Available:
   - LDA Interview: ✅
   - Code Interview: ✅

📋 Data Summary:
   - LinkedIn Claims: 60
   - Resume Claims: 83
   - Job Description Claims: 21
   - Lies Detected: 0
   - Hirability Score: 75.5/100 (Hire)
   - Code Interview Candidate: harsh
   - Final Score: 34
============================================================
```

## Error Handling

The script includes comprehensive error handling:

- ✅ Gracefully handles missing log files
- ✅ Continues processing even if one system's logs are unavailable
- ✅ Provides detailed logging for troubleshooting
- ✅ Validates JSON structure before processing

## Troubleshooting

### No log files found
- Ensure you're running the script from the project root directory
- Check that log files exist in the expected directories
- Verify file permissions

### JSON parsing errors
- Check that log files are valid JSON format
- Ensure files are not corrupted or truncated

### Permission errors
- Make sure the script has read access to log directories
- Ensure write access to create the `consolidated_logs` directory

## Technical Details

### Dependencies
- `json`: JSON parsing and generation
- `os`, `glob`: File system operations
- `datetime`: Timestamp generation
- `pathlib`: Path handling
- `logging`: Comprehensive logging
- `typing`: Type hints for better code quality

### Architecture
- **Modular design** with separate methods for each extraction task
- **Type hints** throughout for better maintainability
- **Comprehensive logging** for debugging and monitoring
- **Error resilience** to handle various edge cases

## Version History

- **v1.0.0**: Initial release with full consolidation functionality
