import { useRef, useState, useEffect } from "react";
import { Box, HStack, VStack, Grid, GridItem } from "@chakra-ui/react";
import { Editor } from "@monaco-editor/react";
import LanguageSelector from "./LanguageSelector";
import QuestionSelector from "./QuestionSelector";
import QuestionDisplay from "./QuestionDisplay";
import TestRunner from "./TestRunner";
import { CODE_SNIPPETS, PROBLEM_BOILERPLATES } from "../constants";
import questionsData from "../data/questions.json";

const CodeEditor = () => {
  const editorRef = useRef();
  const [value, setValue] = useState("");
  const [language, setLanguage] = useState("javascript");
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [questions] = useState(questionsData);
  
  // Check if in interview mode (URL parameter or specific conditions)
  const isInterviewMode = new URLSearchParams(window.location.search).get('interview') === 'true';

  const onMount = (editor) => {
    editorRef.current = editor;
    editor.focus();
  };

  const onLanguageSelect = (newLanguage) => {
    setLanguage(newLanguage);
    updateEditorCode(newLanguage, selectedQuestion);
  };

  const onQuestionSelect = (question) => {
    setSelectedQuestion(question);
    updateEditorCode(language, question);
  };

  const updateEditorCode = (lang, question) => {
    if (question && PROBLEM_BOILERPLATES[question.id] && PROBLEM_BOILERPLATES[question.id][lang]) {
      setValue(PROBLEM_BOILERPLATES[question.id][lang]);
    } else {
      setValue(CODE_SNIPPETS[lang]);
    }
  };

  // Initialize with first question
  useEffect(() => {
    if (questions.length > 0 && !selectedQuestion) {
      const firstQuestion = questions[0];
      setSelectedQuestion(firstQuestion);
      updateEditorCode(language, firstQuestion);
    }
  }, [questions, selectedQuestion, language]);

  // Listen for external question changes (from interview system)
  useEffect(() => {
    const handleSetQuestion = (event) => {
      const questionId = event.detail;
      const question = questions.find(q => q.id === questionId);
      if (question) {
        setSelectedQuestion(question);
        updateEditorCode(language, question);
        console.log(`Question set to: ${question.title}`);
      }
    };

    window.addEventListener('setQuestion', handleSetQuestion);
    return () => window.removeEventListener('setQuestion', handleSetQuestion);
  }, [questions, language]);

  return (
    <Box h="100vh" p={4}>
      <Grid templateColumns="1fr 2fr 1fr" gap={4} h="100%">
        {/* Left Panel - Question Display */}
        <GridItem>
          <VStack spacing={4} h="100%">
            <QuestionSelector
              questions={questions}
              selectedQuestion={selectedQuestion}
              onSelect={onQuestionSelect}
              disabled={isInterviewMode}
            />
            <Box flex="1" w="100%" minH="0">
              <QuestionDisplay question={selectedQuestion} />
            </Box>
          </VStack>
        </GridItem>

        {/* Middle Panel - Code Editor */}
        <GridItem>
          <VStack spacing={4} h="100%">
            <LanguageSelector language={language} onSelect={onLanguageSelect} />
            <Box w="100%" flex="1" minH="0">
              <Editor
                options={{
                  minimap: {
                    enabled: false,
                  },
                  fontSize: 14,
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
                height="100%"
                theme="vs-dark"
                language={language}
                onMount={onMount}
                value={value}
                onChange={(value) => setValue(value)}
              />
            </Box>
          </VStack>
        </GridItem>

        {/* Right Panel - Test Runner */}
        <GridItem>
          <Box h="100%">
            <TestRunner
              editorRef={editorRef}
              language={language}
              question={selectedQuestion}
            />
          </Box>
        </GridItem>
      </Grid>
    </Box>
  );
};
export default CodeEditor;
