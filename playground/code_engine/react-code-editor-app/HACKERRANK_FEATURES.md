# HackerRank-Type Platform Features

This React code editor has been enhanced to function as a coding challenge platform similar to HackerRank, LeetCode, or GeeksforGeeks.

## 🚀 Features Implemented

### 1. **Problem Selection System**
- Dropdown menu to select from available coding problems
- Problems are stored in JSON format with metadata
- Each problem includes:
  - Title and difficulty level
  - Problem description
  - Examples with input/output
  - Constraints
  - Test cases with expected outputs

### 2. **Multi-Language Boilerplate Code**
- Pre-written driver/boilerplate code for all supported languages:
  - JavaScript
  - Python  
  - Java
  - C#
  - PHP
- Each boilerplate includes:
  - Problem description as comments
  - Function/class signature to implement
  - Input parsing logic
  - Output formatting logic
  - Clear separation between user code and test framework

### 3. **Test Case Execution**
- Automated test case runner
- Executes user code against multiple test cases
- Compares actual output with expected output
- Handles different output formats (arrays, booleans, numbers)

### 4. **Score Display**
- Real-time scoring: "x/y tests passed"
- Progress bar showing percentage of tests passed
- Color-coded results (green for pass, red for fail)
- Individual test case breakdown

### 5. **Three-Panel Layout**
- **Left Panel**: Problem description and examples
- **Middle Panel**: Code editor with syntax highlighting
- **Right Panel**: Test results and submission interface

## 📁 File Structure

```
src/
├── components/
│   ├── CodeEditor.jsx          # Main component with 3-panel layout
│   ├── QuestionDisplay.jsx     # Shows problem description
│   ├── QuestionSelector.jsx    # Problem selection dropdown
│   ├── TestRunner.jsx          # Test execution and results
│   ├── LanguageSelector.jsx    # Language selection
│   └── Output.jsx              # Original output component
├── data/
│   └── questions.json          # Problem database
├── constants.js                # Boilerplate code templates
└── api.js                      # Code execution API
```

## 🎯 Sample Problems Included

1. **Two Sum** (Easy)
   - Find indices of two numbers that add up to target
   - Test cases with array inputs and index outputs

2. **Palindrome Number** (Easy)
   - Check if integer is palindrome
   - Test cases with boolean outputs

3. **Reverse Integer** (Medium)
   - Reverse digits of an integer
   - Test cases with integer outputs

## 🔧 How to Use

1. **Select a Problem**: Use the dropdown to choose a coding problem
2. **Choose Language**: Select your preferred programming language
3. **Write Solution**: Implement the solution function in the editor
4. **Submit**: Click "Submit Solution" to run all test cases
5. **View Results**: See your score and individual test case results

## 🧪 Test Case Format

Each problem in `questions.json` includes:

```json
{
  "id": 1,
  "title": "Problem Name",
  "difficulty": "Easy|Medium|Hard",
  "description": "Problem description...",
  "examples": [...],
  "constraints": [...],
  "testCases": [
    {
      "input": "input string",
      "expectedOutput": "expected output string"
    }
  ]
}
```

## 🎨 UI Features

- **Dark Theme**: Professional coding environment
- **Syntax Highlighting**: Monaco Editor with VS Code experience
- **Responsive Design**: Optimal layout for coding challenges
- **Progress Indicators**: Visual feedback on test progress
- **Expandable Results**: Detailed view of each test case
- **Error Handling**: Clear display of compilation/runtime errors

## 🚀 Getting Started

1. Install dependencies: `npm install`
2. Start development server: `npm run dev`
3. Open browser to localhost (usually :5173)
4. Select a problem and start coding!

## 🔄 Adding New Problems

To add new problems:

1. Add problem data to `src/data/questions.json`
2. Add boilerplate code to `src/constants.js` in `PROBLEM_BOILERPLATES`
3. Use the same ID for both the question and boilerplate

The platform will automatically load and display new problems!
