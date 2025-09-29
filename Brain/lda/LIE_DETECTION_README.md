# LDA Lie Detection & Nudging System

## Overview

The LDA (Lie Detection & Analysis) system now includes comprehensive lie detection and logging functionality that:

1. **Detects lies** during interviews by comparing candidate statements to verified facts from their resume/LinkedIn
2. **Nudges candidates** to elaborate when lies are detected
3. **Logs lies and elaborations** in interview summary files under a new "lies" key

## How It Works

### 1. Lie Detection
- The `LieDetectionAgent` analyzes each candidate response
- Compares claims against verified facts from resume/LinkedIn data
- Flags potential lies with confidence scores and reasoning
- Only flags **direct contradictions** (e.g., "worked at Google" vs resume showing "worked at Microsoft")

### 2. Nudging System
- When a lie is detected above the confidence threshold, the interviewer automatically nudges
- Nudges escalate in intensity: polite → firm → aggressive → final_warning
- The `InterviewerAgent.deliver_nudge()` method handles nudge generation and delivery

### 3. Elaboration Capture
- After delivering a nudge, the system listens for the candidate's elaboration
- Captures their explanation or marks as "(No elaboration provided)"
- Adds the elaboration to the conversation history

### 4. Enhanced Logging
Interview summary JSON files now include a new `"lies"` key with structure:

```json
{
  "summary": { ... },
  "conversation_history": [ ... ],
  "knowledge_base": { ... },
  "lies": [
    {
      "lie": "The false claim made by candidate",
      "explanation_given_by_candidate": "Their elaboration or '(No elaboration provided)'",
      "confidence": 0.95,
      "reasoning": "Why this was flagged as a lie",
      "category": "experience|education|skills|personal|other"
    }
  ]
}
```

## Key Features

✅ **Automatic lie detection** during interviews  
✅ **Intelligent nudging** with escalating intensity  
✅ **Elaboration capture** - records candidate explanations  
✅ **Rich context logging** - confidence, reasoning, category for each lie  
✅ **Multiple lies support** - handles multiple lies per interview  
✅ **Graceful handling** - works when no elaboration is provided  
✅ **Fallback detection** - captures lies even when interviews end before nudging  
✅ **Robust logging** - multiple detection mechanisms ensure no lies are missed  
✅ **JSON serializable** - all data properly formatted for storage  

## Configuration

Key configuration in `config.py`:
- `LIE_CONFIDENCE_THRESHOLD`: Minimum confidence score to trigger nudging (default: configurable)

## Code Changes Made

### Main Interview Loop (`main.py`)
- Added `lies_detected: List[Dict[str, str]] = []` to track lies
- Enhanced lie detection section (lines ~405-440) to:
  - Log detected lies with warning messages
  - Listen for candidate elaborations after nudges
  - Store lie + elaboration data with full context
- Added `"lies": lies_detected` to interview summary JSON
- **Added fallback detection mechanisms**:
  - Captures lies detected in interviewer evaluations (even when formal lie detection doesn't trigger)
  - Processes unhandled lies when interviews end due to timeout
  - Ensures no lies are missed due to timing issues

### Existing Components Used
- `LieDetectionAgent` - Already existed for lie detection
- `InterviewerAgent.deliver_nudge()` - Already existed for nudging
- `ClaimAnalysis` model - Already provided rich lie context

## Testing

Run tests to verify functionality:
```bash
python tests/test_lie_detection_logging.py
```

Run demo to see it in action:
```bash
cd Brain/lda && python demo_lie_detection.py
```

## Example Usage

During an interview, if a candidate says:
> "I worked as a Senior Software Engineer at Google for 5 years"

But their resume shows:
> "Junior Developer at Microsoft (2 years)"

The system will:
1. **Detect** the contradiction (confidence: 0.95)
2. **Nudge**: "I need to pause here... this doesn't align with the information I have..."
3. **Listen** for elaboration: "Oh, I meant Microsoft, not Google. I misspoke."
4. **Log** both the lie and elaboration in the interview summary

## Benefits

- **Improved interview quality** - Catches and addresses inconsistencies in real-time
- **Better candidate assessment** - Records how candidates handle being questioned about inconsistencies  
- **Enhanced data collection** - Rich context about lies and candidate responses
- **Audit trail** - Complete record of detected lies and explanations for review

## Future Enhancements

Potential improvements:
- Severity-based nudging strategies
- Lie pattern analysis across multiple interviews
- Integration with hiring decision algorithms
- Real-time lie detection metrics and dashboards
