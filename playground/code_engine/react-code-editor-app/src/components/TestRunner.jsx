import { useState } from "react";
import {
  Box,
  Button,
  Text,
  VStack,
  HStack,
  Progress,
  Badge,
  useToast,
  Spinner,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Code,
} from "@chakra-ui/react";
import { executeCode } from "../api";

const TestRunner = ({ editorRef, language, question }) => {
  const toast = useToast();
  const [testResults, setTestResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [score, setScore] = useState({ passed: 0, total: 0 });

  const runTests = async () => {
    if (!question || !question.testCases) {
      toast({
        title: "No test cases available",
        description: "Please select a question first",
        status: "warning",
        duration: 3000,
      });
      return;
    }

    const sourceCode = editorRef.current?.getValue();
    if (!sourceCode) {
      toast({
        title: "No code to test",
        description: "Please write some code first",
        status: "warning",
        duration: 3000,
      });
      return;
    }

    setIsRunning(true);
    setTestResults(null);

    try {
      const results = [];
      let passedCount = 0;

      for (let i = 0; i < question.testCases.length; i++) {
        const testCase = question.testCases[i];
        
        try {
          const { run: result } = await executeCode(language, sourceCode, testCase.input);
          
          const actualOutput = result.output?.trim() || "";
          const expectedOutput = testCase.expectedOutput?.trim() || "";
          
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
        } catch (error) {
          results.push({
            testCase: i + 1,
            input: testCase.input,
            expected: testCase.expectedOutput,
            actual: "",
            passed: false,
            error: error.message,
          });
        }
      }

      setTestResults(results);
      setScore({ passed: passedCount, total: question.testCases.length });

      // Show success/failure toast
      if (passedCount === question.testCases.length) {
        toast({
          title: "All tests passed! 🎉",
          description: `Perfect score: ${passedCount}/${question.testCases.length}`,
          status: "success",
          duration: 5000,
        });
      } else {
        toast({
          title: "Some tests failed",
          description: `Score: ${passedCount}/${question.testCases.length}`,
          status: "warning",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error("Test execution error:", error);
      toast({
        title: "Execution Error",
        description: error.message || "Failed to run tests",
        status: "error",
        duration: 6000,
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Normalize output for comparison (handle arrays, booleans, etc.)
  const normalizeOutput = (output) => {
    if (!output) return "";
    
    // Remove extra whitespace and newlines
    let normalized = output.trim();
    
    // Handle array format differences [0,1] vs [0, 1]
    normalized = normalized.replace(/\s*,\s*/g, ', ');
    
    // Handle boolean case differences
    if (normalized.toLowerCase() === 'true') return 'true';
    if (normalized.toLowerCase() === 'false') return 'false';
    
    return normalized;
  };

  const getProgressColor = () => {
    if (!testResults) return "blue";
    const percentage = (score.passed / score.total) * 100;
    if (percentage === 100) return "green";
    if (percentage >= 50) return "yellow";
    return "red";
  };

  return (
    <Box w="100%" h="100%">
      <VStack spacing={4} align="stretch" h="100%">
        {/* Header with Submit Button */}
        <HStack justify="space-between" align="center">
          <Text fontSize="lg" fontWeight="bold" color="white">
            Test Results
          </Text>
          <Button
            colorScheme="blue"
            onClick={runTests}
            isLoading={isRunning}
            loadingText="Running Tests"
            disabled={!question || !question.testCases}
          >
            Submit Solution
          </Button>
        </HStack>

        {/* Score Display */}
        {testResults && (
          <Box p={4} bg="gray.700" borderRadius="md">
            <HStack justify="space-between" align="center" mb={2}>
              <Text color="white" fontWeight="bold">
                Score: {score.passed}/{score.total}
              </Text>
              <Badge
                colorScheme={score.passed === score.total ? "green" : "red"}
                variant="solid"
                fontSize="sm"
              >
                {score.passed === score.total ? "PASSED" : "FAILED"}
              </Badge>
            </HStack>
            <Progress
              value={(score.passed / score.total) * 100}
              colorScheme={getProgressColor()}
              size="lg"
              borderRadius="md"
            />
            <Text fontSize="sm" color="gray.300" mt={1}>
              {((score.passed / score.total) * 100).toFixed(1)}% tests passed
            </Text>
          </Box>
        )}

        {/* Loading State */}
        {isRunning && (
          <Box textAlign="center" p={8}>
            <Spinner size="lg" color="blue.400" />
            <Text color="gray.300" mt={4}>
              Running test cases...
            </Text>
          </Box>
        )}

        {/* Test Results */}
        {testResults && !isRunning && (
          <Box flex="1" overflowY="auto">
            <Accordion allowMultiple>
              {testResults.map((result, index) => (
                <AccordionItem key={index} border="1px solid" borderColor="gray.600" mb={2}>
                  <AccordionButton bg={result.passed ? "green.800" : "red.800"} _hover={{ bg: result.passed ? "green.700" : "red.700" }}>
                    <Box flex="1" textAlign="left">
                      <HStack>
                        <Text color="white" fontWeight="bold">
                          Test Case {result.testCase}
                        </Text>
                        <Badge colorScheme={result.passed ? "green" : "red"} variant="solid">
                          {result.passed ? "PASS" : "FAIL"}
                        </Badge>
                      </HStack>
                    </Box>
                    <AccordionIcon color="white" />
                  </AccordionButton>
                  <AccordionPanel bg="gray.800" color="white">
                    <VStack align="start" spacing={3}>
                      <Box>
                        <Text fontWeight="bold" color="blue.300">Input:</Text>
                        <Code bg="gray.700" color="gray.200" p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                          {result.input}
                        </Code>
                      </Box>
                      
                      <Box>
                        <Text fontWeight="bold" color="green.300">Expected Output:</Text>
                        <Code bg="gray.700" color="gray.200" p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                          {result.expected}
                        </Code>
                      </Box>
                      
                      <Box>
                        <Text fontWeight="bold" color={result.passed ? "green.300" : "red.300"}>
                          Your Output:
                        </Text>
                        <Code 
                          bg="gray.700" 
                          color={result.passed ? "gray.200" : "red.300"} 
                          p={2} 
                          borderRadius="md" 
                          display="block" 
                          whiteSpace="pre-wrap"
                        >
                          {result.actual || "(no output)"}
                        </Code>
                      </Box>

                      {result.error && (
                        <Box>
                          <Text fontWeight="bold" color="red.300">Error:</Text>
                          <Code bg="red.900" color="red.200" p={2} borderRadius="md" display="block" whiteSpace="pre-wrap">
                            {result.error}
                          </Code>
                        </Box>
                      )}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>
          </Box>
        )}

        {/* Empty State */}
        {!testResults && !isRunning && (
          <Box textAlign="center" p={8} color="gray.400">
            <Text>Click "Submit Solution" to run test cases</Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default TestRunner;
