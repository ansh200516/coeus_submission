'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { executeCode, ExecuteCodeResponse } from '@/lib/coding-engine/api';
import { Question } from '@/lib/coding-engine/types';
import { TEST_BOILERPLATES } from '@/lib/coding-engine/boilerplates';

interface TestRunnerProps {
  editorRef: React.MutableRefObject<any | null>;
  language: string;
  question: Question | null;
  interviewSession?: string | null;
  onTestComplete?: (results: TestResult[], score: { passed: number; total: number }) => void;
}

interface TestResult {
  testCase: number;
  input: string;
  expected: string;
  actual: string;
  passed: boolean;
  error: string | null;
}

const TestRunner = ({ editorRef, language, question, interviewSession, onTestComplete }: TestRunnerProps) => {
  const [testResults, setTestResults] = useState<TestResult[] | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [score, setScore] = useState({ passed: 0, total: 0 });

  const runTests = async () => {
    if (!question || !question.testCases) {
      toast.warning('No test cases available', {
        description: 'Please select a question first',
      });
      return;
    }

    const userCode = editorRef.current?.getValue();
    if (!userCode) {
      toast.warning('No code to test', {
        description: 'Please write some code first',
      });
      return;
    }

    setIsRunning(true);
    setTestResults(null);

    try {
      const results: TestResult[] = [];
      let passedCount = 0;

      // Get the appropriate test boilerplate based on problem type
      const problemType = question.problemType || 'sum'; // Default to sum if not specified
      const testBoilerplates = TEST_BOILERPLATES[problemType as keyof typeof TEST_BOILERPLATES] || {};
      const testBoilerplate = testBoilerplates[language as keyof typeof testBoilerplates] || '';
      
      // For Java and C#, we need to insert the user code into the Solution class
      let fullCode = userCode;
      
      if (language === 'java') {
        // Extract the solution method from user code
        const methodMatch = userCode.match(/public\s+(?:\w+(?:<[^>]+>)?(?:\[\])?)\s+solution\s*\([^)]*\)[^{]*\{[\s\S]*?\n\s*\}/);
        if (methodMatch) {
          // Insert the solution method into the test boilerplate
          fullCode = testBoilerplate.replace('// User code will be inserted here', methodMatch[0]);
        } else {
          // If no match, use the user code as is (might cause errors)
          fullCode = userCode + testBoilerplate;
        }
      } else if (language === 'csharp') {
        // Extract the solution method from user code
        const methodMatch = userCode.match(/public\s+(?:\w+(?:<[^>]+>)?(?:\[\])?)\s+Solution\s*\([^)]*\)[^{]*\{[\s\S]*?\n\s*\}/);
        if (methodMatch) {
          // Insert the solution method into the test boilerplate
          fullCode = testBoilerplate.replace('// User code will be inserted here', methodMatch[0]);
        } else {
          // If no match, use the user code as is (might cause errors)
          fullCode = userCode + testBoilerplate;
        }
      } else {
        // For other languages, simply concatenate
        fullCode = userCode + testBoilerplate;
      }

      for (let i = 0; i < question.testCases.length; i++) {
        const testCase = question.testCases[i];

        try {
          const { run: result }: ExecuteCodeResponse = await executeCode(language, fullCode, testCase.input);

          const actualOutput = result.output?.trim() || '';
          const expectedOutput = testCase.expectedOutput?.trim() || '';

          // Handle different output formats and normalize them
          const normalizedActual = normalizeOutput(actualOutput);
          const normalizedExpected = normalizeOutput(expectedOutput);

          const passed = normalizedActual === normalizedExpected;
          if (passed) passedCount++;

          results.push({
            testCase: i + 1,
            input: testCase.input,
            expected: expectedOutput,
            actual: actualOutput,
            passed,
            error: result.stderr || null,
          });
        } catch (error: any) {
          results.push({
            testCase: i + 1,
            input: testCase.input,
            expected: testCase.expectedOutput,
            actual: '',
            passed: false,
            error: error.message,
          });
        }
      }

      setTestResults(results);
      setScore({ passed: passedCount, total: question.testCases.length });

      // Show success/failure toast
      if (passedCount === question.testCases.length) {
        toast.success('All tests passed!', {
          description: `Perfect score: ${passedCount}/${question.testCases.length}`,
        });
      } else {
        toast.warning('Some tests failed', {
          description: `Score: ${passedCount}/${question.testCases.length}`,
        });
      }

      // Notify interview agent of test completion
      if (onTestComplete) {
        onTestComplete(results, { passed: passedCount, total: question.testCases.length });
      }
    } catch (error: any) {
      console.error('Test execution error:', error);
      toast.error('Execution Error', {
        description: error.message || 'Failed to run tests. Please check your internet connection and try again.',
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Normalize output for comparison (handle arrays, booleans, etc.)
  const normalizeOutput = (output: string) => {
    if (!output) return '';

    // Remove extra whitespace and newlines
    let normalized = output.trim();

    // Handle array format differences [0,1] vs [0, 1]
    normalized = normalized.replace(/\s*,\s*/g, ', ');

    // Handle boolean case differences
    if (normalized.toLowerCase() === 'true') return 'true';
    if (normalized.toLowerCase() === 'false') return 'false';

    return normalized;
  };

  const [activeTestCase, setActiveTestCase] = useState(0);

  return (
    <div
      className="h-full flex flex-col bg-background/95 backdrop-blur-sm border-l border-border/50"
      data-test-component
      ref={(el) => {
        if (el) {
          (el as any).runTests = runTests;
        }
      }}
    >
      {/* Test Case Tabs */}
      <div className="flex border-b border-border/30 overflow-x-auto scrollbar-hide bg-background/50">
        {question?.testCases && question.testCases.map((_, index) => (
          <button
            key={index}
            className={`px-6 py-3 text-sm font-medium whitespace-nowrap transition-all duration-200 flex items-center gap-2 ${
              activeTestCase === index
                ? 'text-foreground border-b-2 border-blue-400 bg-blue-400/10'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            }`}
            onClick={() => setActiveTestCase(index)}
          >
            Test Case {index + 1}
            {testResults && testResults[index] && (
              testResults[index]?.passed ? 
                <CheckCircle className="h-4 w-4 text-green-400" /> : 
                <XCircle className="h-4 w-4 text-red-400" />
            )}
          </button>
        ))}
      </div>

      {/* Test Case Content */}
      <div className="flex-1 h-0 overflow-hidden">
        {/* Loading State */}
        {isRunning && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent mx-auto mb-2"></div>
              <p className="text-sm text-muted-foreground">Running...</p>
            </div>
          </div>
        )}

        {question?.testCases && question.testCases.length > 0 ? (
          <div className="h-full p-6 flex flex-col">
            {/* Test Case Details */}
            <div className="flex-grow overflow-y-auto mb-6">
              <div className="space-y-6">
                {/* Input */}
                <div className="text-sm">
                  <div className="font-medium mb-3 text-foreground">Input</div>
                  <div className="bg-muted/30 border border-border/30 p-4 rounded-lg font-mono text-xs text-foreground/90">
                    {question.testCases[activeTestCase].input}
                  </div>
                </div>
                
                {/* Expected Output */}
                <div className="text-sm">
                  <div className="font-medium mb-3 text-foreground">Expected Output</div>
                  <div className="bg-muted/30 border border-border/30 p-4 rounded-lg font-mono text-xs text-foreground/90">
                    {question.testCases[activeTestCase].expectedOutput}
                  </div>
                </div>

                {/* Results (if available) */}
                {testResults && testResults[activeTestCase] && (
                  <>
                    <div className="text-sm">
                      <div className="font-medium mb-3 flex items-center gap-3">
                        Your Output
                        <Badge 
                          variant={testResults[activeTestCase].passed ? "default" : "destructive"} 
                          className="rounded-lg font-mono text-xs px-3 py-1"
                        >
                          {testResults[activeTestCase].passed ? (
                            <><CheckCircle className="h-3 w-3 mr-1" />Passed</>
                          ) : (
                            <><XCircle className="h-3 w-3 mr-1" />Failed</>
                          )}
                        </Badge>
                      </div>
                      <div className={`border p-4 rounded-lg font-mono text-xs ${
                        testResults[activeTestCase].passed 
                          ? 'bg-green-400/5 border-green-400/20 text-green-200' 
                          : 'bg-red-400/5 border-red-400/20 text-red-200'
                      }`}>
                        {testResults[activeTestCase].actual || '(no output)'}
                      </div>
                    </div>
                    
                    {/* Error (if any) */}
                    {testResults[activeTestCase].error && (
                      <div className="text-sm">
                        <div className="font-medium text-red-400 mb-3 flex items-center gap-2">
                          <AlertCircle className="h-4 w-4" />
                          Error
                        </div>
                        <div className="bg-red-400/5 border border-red-400/20 p-4 rounded-lg font-mono text-red-300 text-xs">
                          {testResults[activeTestCase].error}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
            
            {/* Summary (if results available) */}
            {testResults && (
              <div className="mb-6">
                <div className={`text-sm font-semibold flex items-center gap-2 ${
                  score.passed === score.total ? 'text-green-400' : 'text-orange-400'
                }`}>
                  {score.passed === score.total ? (
                    <><CheckCircle className="h-4 w-4" />All Tests Passed</>
                  ) : (
                    <><AlertCircle className="h-4 w-4" />{score.passed}/{score.total} Tests Passed</>
                  )}
                </div>
              </div>
            )}
            
            {/* Run/Submit Buttons */}
            <div className="flex gap-3">
              <Button
                size="sm"
                variant="outline"
                onClick={runTests}
                disabled={isRunning}
                className="text-xs border border-border/30 rounded-lg font-mono hover:bg-muted/30 transition-all duration-200"
              >
                {isRunning ? 'Running...' : 'Run Tests'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={runTests}
                disabled={isRunning}
                className="text-xs bg-green-500/10 hover:bg-green-500 text-green-400 hover:text-black border-green-500/30 hover:border-green-500 border rounded-lg font-mono transition-all duration-200"
              >
                Submit
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            No test cases available
          </div>
        )}
      </div>
    </div>
  );
};

export default TestRunner;
