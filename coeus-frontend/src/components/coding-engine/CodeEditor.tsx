"use client";

import { useRef, useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import QuestionTitle from "./QuestionTitle";
import QuestionDisplay from "./QuestionDisplay";
import TestRunner from "./TestRunner";
import Header from "./Header";
import {
  CODE_SNIPPETS,
  LANGUAGE_VERSIONS,
} from "@/lib/coding-engine/constants";
import {
  USER_BOILERPLATES,
  TEST_BOILERPLATES,
} from "@/lib/coding-engine/boilerplates";
import { Question } from "@/lib/coding-engine/types";
import questionsData from "@/data/questions.json";

const CodeEditor = () => {
  const editorRef = useRef<any>(null);
  const [value, setValue] = useState("");
  const [language, setLanguage] = useState("python");
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(
    null
  );
  const [questions] = useState<Question[]>(questionsData);
  const [interviewSession, setInterviewSession] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  // Expose interview data to window object for agent access
  useEffect(() => {
    if (typeof window !== "undefined" && interviewSession) {
      (window as any).interviewData = {
        sessionId: interviewSession,
        currentQuestion: selectedQuestion,
        language,
        questions,
        getCurrentCode: () => editorRef.current?.getValue(),
        getTestResults: () => {
          try {
            const stored = sessionStorage.getItem(
              `interview_session_${interviewSession}`
            );
            return stored ? JSON.parse(stored) : null;
          } catch {
            return null;
          }
        },
      };
    }
  }, [interviewSession, selectedQuestion, language, questions]);

  const onMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    editor.focus();

    // Add Shift+Enter keyboard shortcut for submit
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
      handleSubmit();
    });
  };

  const onLanguageSelect = (newLanguage: string) => {
    setLanguage(newLanguage);
    updateEditorCode(newLanguage, selectedQuestion);
  };

  const updateEditorCode = (lang: string, question: Question | null) => {
    if (question && question.problemType) {
      // Use our new user-facing boilerplates based on problem type
      const problemType = question.problemType;
      if (problemType in USER_BOILERPLATES) {
        const boilerplate =
          USER_BOILERPLATES[problemType as keyof typeof USER_BOILERPLATES];
        if (boilerplate && lang in boilerplate) {
          setValue(boilerplate[lang as keyof typeof boilerplate]);
          return;
        }
      }
    }

    // Fallback to generic code snippets
    setValue(CODE_SNIPPETS[lang as keyof typeof CODE_SNIPPETS]);
  };

  // Initialize question from URL or API (no page reload)
  useEffect(() => {
    const initializeQuestion = async () => {
      try {
        // Don't initialize if we already have a selected question
        if (selectedQuestion) {
          return;
        }

        const urlParams = new URLSearchParams(window.location.search);
        const questionId = urlParams.get("question");

        if (questionId) {
          // Use question from URL if provided
          const parsedQuestionId = parseInt(questionId);
          if (!isNaN(parsedQuestionId)) {
            const question = questions.find((q) => q.id === parsedQuestionId);
            if (question) {
              console.log("Loading question from URL:", question.title);
              setSelectedQuestion(question);
              updateEditorCode(language, question);

              // Track interview session if provided
              const sessionId = urlParams.get("session");
              if (sessionId) {
                setInterviewSession(sessionId);
                console.log("Interview session started:", sessionId);
              } else {
                // Generate session ID if not present
                const newSessionId = `session_${Date.now()}_${Math.random()
                  .toString(36)
                  .substr(2, 9)}`;
                setInterviewSession(newSessionId);
                console.log("Generated new session ID:", newSessionId);
              }

              return;
            }
          }
        }

        // No URL parameter or question not found - call API to select question
        console.log(
          "No valid question in URL, calling API to select question..."
        );

        try {
          const response = await fetch(
            "http://localhost:8001/questions/select_question",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
              },
              body: JSON.stringify({
                difficulty: "Easy", // Default to Easy difficulty
              }),
            }
          );

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const result = await response.json();
          console.log("✅ Question selected from API:", result);

          if (result.question && result.question.id) {
            // Find the question in local data and set it
            const apiQuestion = questions.find(
              (q) => q.id === result.question.id
            );
            if (apiQuestion) {
              console.log("Setting question from API:", apiQuestion.title);
              setSelectedQuestion(apiQuestion);
              updateEditorCode(language, apiQuestion);

              // Update URL without reload
              const newUrl = new URL(window.location.href);
              newUrl.searchParams.set(
                "question",
                result.question.id.toString()
              );

              // Generate session ID if not present
              let sessionId = newUrl.searchParams.get("session");
              if (!sessionId) {
                sessionId = `session_${Date.now()}_${Math.random()
                  .toString(36)
                  .substr(2, 9)}`;
                newUrl.searchParams.set("session", sessionId);
                setInterviewSession(sessionId);
                console.log("Generated new session ID:", sessionId);
              }

              // Update URL without reload
              window.history.pushState({}, "", newUrl.toString());
              console.log("Updated URL without reload:", newUrl.toString());
              return;
            }
          }
        } catch (error) {
          console.error("❌ Failed to select question from API:", error);
          // Fall back to first question from local data
        }

        // Fallback to first question if API fails or no questions
        if (questions.length > 0) {
          console.log("Falling back to first question");
          const firstQuestion = questions[0];
          setSelectedQuestion(firstQuestion);
          updateEditorCode(language, firstQuestion);

          // Generate a default session ID for tracking
          const defaultSessionId = `session_${Date.now()}_${Math.random()
            .toString(36)
            .substr(2, 9)}`;
          setInterviewSession(defaultSessionId);
          console.log("Default interview session created:", defaultSessionId);
        }
      } catch (error) {
        console.error("Error initializing question:", error);
        // Fallback to first question on error
        if (questions.length > 0) {
          const firstQuestion = questions[0];
          setSelectedQuestion(firstQuestion);
          updateEditorCode(language, firstQuestion);
        }
      }
    };

    // Only initialize if we have questions loaded and no selected question
    if (questions.length > 0 && !selectedQuestion) {
      initializeQuestion();
    }
  }, [questions, selectedQuestion, language]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case "easy":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "hard":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const handleSubmit = async () => {
    console.log("=== CODE SUBMISSION INITIATED ===");
    console.log("Current session ID:", interviewSession);
    console.log("Selected question:", selectedQuestion?.title);
    console.log("Programming language:", language);

    const currentCode = editorRef.current?.getValue();
    console.log("Code length:", currentCode?.length || 0);
    console.log(
      "Code content preview:",
      currentCode?.substring(0, 100) + "..."
    );

    // Code submission - WebSocket functionality removed

    const testRunnerElement = document.querySelector(
      "[data-testrunner]"
    ) as any;
    if (testRunnerElement && testRunnerElement.runTests) {
      console.log("Triggering test execution");
      setIsSubmitting(true);
      testRunnerElement.runTests();
    } else {
      console.error("Test runner element not found");
    }

    console.log("=== CODE SUBMISSION PROCESS COMPLETED ===");
  };

  const moveToNextQuestion = async () => {
    if (!selectedQuestion) return;

    console.log("Moving to next question...");

    try {
      // Determine next difficulty level
      const currentDifficulty = selectedQuestion.difficulty;
      let nextDifficulty = "Easy";

      if (currentDifficulty === "Easy") {
        nextDifficulty = "Medium";
      } else if (currentDifficulty === "Medium") {
        nextDifficulty = "Hard";
      } else {
        nextDifficulty = "Easy"; // Cycle back to Easy after Hard
      }

      console.log(`Selecting next question with difficulty: ${nextDifficulty}`);

      // Call API to select next question
      const response = await fetch(
        "http://localhost:8001/questions/select_question",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            difficulty: nextDifficulty,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log("✅ Next question selected from API:", result);

      if (result.question && result.question.id) {
        // Find the question in local data and set it
        const apiQuestion = questions.find((q) => q.id === result.question.id);
        if (apiQuestion) {
          console.log("Setting next question:", apiQuestion.title);
          setSelectedQuestion(apiQuestion);
          updateEditorCode(language, apiQuestion);

          // Update URL without reload
          const url = new URL(window.location.href);
          url.searchParams.set("question", apiQuestion.id.toString());
          window.history.pushState({}, "", url.toString());
          console.log("Updated URL for next question:", url.toString());
          return;
        }
      }
    } catch (error) {
      console.error("❌ Failed to get next question from API:", error);
    }

    // Fallback to sequential navigation if API fails
    console.log("Falling back to sequential navigation");
    const currentIndex = questions.findIndex(
      (q) => q.id === selectedQuestion.id
    );
    const nextIndex = currentIndex + 1;

    if (nextIndex < questions.length) {
      const nextQuestion = questions[nextIndex];
      setSelectedQuestion(nextQuestion);
      updateEditorCode(language, nextQuestion);

      // Update URL to reflect new question
      const url = new URL(window.location.href);
      url.searchParams.set("question", nextQuestion.id.toString());
      window.history.pushState({}, "", url.toString());
      console.log("Fallback: moved to next question sequentially");
    } else {
      console.log("No more questions available");
    }
  };

  const handleTimeUp = () => {
    console.log("Time is up! Auto-submitting...");
    handleSubmit();
  };

  const handleStart = async () => {
    console.log("=== INTERVIEW START INITIATED ===");
    console.log("Timestamp:", new Date().toISOString());

    // Prevent multiple simultaneous start attempts
    if (isStarting) {
      console.log("Interview start already in progress...");
      return;
    }

    setIsStarting(true);

    try {
      // Get the current session ID or create one
      let sessionId = interviewSession;
      if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random()
          .toString(36)
          .substr(2, 9)}`;
        setInterviewSession(sessionId);

        // Update URL to include session
        const url = new URL(window.location.href);
        url.searchParams.set("session", sessionId);
        window.history.pushState({}, "", url.toString());
      }

      console.log("Session ID:", sessionId);
      console.log("Current question:", selectedQuestion?.title);
      console.log("Language:", language);

      // Get candidate name (prompt user or use session ID as fallback)
      let candidateName = sessionId; // Default fallback
      let duration = 300; // Default 5 minutes

      try {
        // Try to get candidate name from user
        const userProvidedName = prompt("Enter candidate name (optional):");
        if (userProvidedName && userProvidedName.trim()) {
          candidateName = userProvidedName.trim();
        }

        // Try to get custom duration from user
        const userProvidedDuration = prompt(
          "Enter interview duration in seconds (default: 300):"
        );
        if (userProvidedDuration && userProvidedDuration.trim()) {
          const parsedDuration = parseInt(userProvidedDuration.trim());
          if (!isNaN(parsedDuration) && parsedDuration > 0) {
            duration = parsedDuration;
          }
        }
      } catch (error) {
        console.log("Could not prompt for user input, using defaults");
      }

      // Prepare request data
      const requestData = {
        name: candidateName,
        duration: duration,
        question_id: selectedQuestion?.id || 1, // Send the current question ID
      };

      console.log("Candidate name:", candidateName);
      console.log("Interview duration:", duration, "seconds");
      console.log("Sending request to task controller:", requestData);

      // Call the task controller REST API endpoint
      const response = await fetch("http://localhost:8001/tasks/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(requestData),
      });

      console.log("Response status:", response.status);
      console.log(
        "Response headers:",
        Object.fromEntries(response.headers.entries())
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("API Error Response:", errorText);
        throw new Error(
          `HTTP ${response.status}: ${errorText || response.statusText}`
        );
      }

      const result = await response.json();
      console.log("✅ Interview task started successfully:", result);
      console.log("Task ID:", result.task_id);
      console.log("Status:", result.status);
      console.log("Message:", result.message);

      // Show success feedback to user
      if (typeof window !== "undefined") {
        alert(
          `Interview started successfully!\nTask ID: ${result.task_id}\nStatus: ${result.status}`
        );
      }
    } catch (error) {
      console.error("❌ Failed to start interview task:", error);

      // Show error feedback to user
      if (typeof window !== "undefined") {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error occurred";
        alert(
          `Failed to start interview task:\n${errorMessage}\n\nThe interview interface will continue to work, but background processes may not be available.`
        );
      }

      // Continue with the interview even if the backend call fails
      console.log("Continuing with interview despite API failure...");
    } finally {
      setIsStarting(false);
      console.log("=== INTERVIEW START PROCESS COMPLETED ===");
    }
  };

  const resetCode = () => {
    setValue("");
    updateEditorCode(language, selectedQuestion);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Header
        onTimeUp={handleTimeUp}
        onSubmit={handleSubmit}
        onStart={handleStart}
      />

      {/* Main Content - LeetCode Layout */}
      <div className="flex-1 flex min-h-0">
        {/* Left Panel - Description */}
        <div className="w-1/2 border-r border-border/30 flex flex-col min-h-0">
          {/* Content */}
          <div className="flex-1 flex flex-col min-h-0">
            {/* Question Title */}
            <div className="h-12 px-4 border-b border-border/30 flex-shrink-0 flex items-center">
              <div className="flex items-center justify-between w-full">
                <h1 className="text-xl font-bold text-foreground font-mono">
                  {selectedQuestion?.id}. {selectedQuestion?.title}
                </h1>
                <Badge
                  variant="secondary"
                  className={`${getDifficultyColor(
                    selectedQuestion?.difficulty || "easy"
                  )} rounded-lg font-mono`}
                >
                  {selectedQuestion?.difficulty}
                </Badge>
              </div>
            </div>

            {/* Question Content - Scrollable */}
            <div className="flex-1 overflow-auto">
              <QuestionDisplay question={selectedQuestion} />
            </div>
          </div>
        </div>

        {/* Right Panel - Code */}
        <div className="w-1/2 flex flex-col min-h-0">
          {/* Code Header */}
          <div className="flex items-center justify-between h-12 px-4 border-b border-border/30 flex-shrink-0">
            <div className="flex items-center space-x-4">
              <Select value={language} onValueChange={onLanguageSelect}>
                <SelectTrigger className="w-32 h-8 rounded-lg font-mono">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="rounded-lg font-mono">
                  {Object.entries(LANGUAGE_VERSIONS).map(([lang, version]) => (
                    <SelectItem key={lang} value={lang} className="font-mono">
                      {lang}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <span className="text-sm text-muted-foreground font-mono">
                Auto
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={resetCode}
                className="rounded-lg font-mono"
              >
                ↻ Reset
              </Button>
            </div>
          </div>

          {/* Code Editor - 50% height */}
          <div className="flex-1 relative min-h-0">
            <Editor
              options={{
                minimap: {
                  enabled: false,
                },
                fontSize: 14,
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 16, bottom: 16 },
              }}
              height="100%"
              theme="vs-dark"
              language={language}
              onMount={onMount}
              value={value}
              onChange={(value) => setValue(value || "")}
            />
          </div>
          {/* Test Cases - 50% height */}
          <div className="flex-1 border-border flex-shrink-0 min-h-0">
            <div
              data-testrunner
              ref={(el) => {
                if (el) {
                  (el as any).runTests = async () => {
                    // Trigger test run
                    const testRunnerComponent = document.querySelector(
                      "[data-test-component]"
                    ) as any;
                    if (testRunnerComponent && testRunnerComponent.runTests) {
                      testRunnerComponent.runTests();
                    }
                  };
                }
              }}
            >
              <TestRunner
                editorRef={editorRef}
                language={language}
                question={selectedQuestion}
                interviewSession={interviewSession}
                onTestComplete={(results, score) => {
                  setIsSubmitting(false);

                  console.log("Test completed:", {
                    session: interviewSession,
                    questionId: selectedQuestion?.id,
                    score,
                    results,
                    timestamp: new Date().toISOString(),
                  });

                  if (typeof window !== "undefined") {
                    const sessionData = {
                      sessionId: interviewSession,
                      questionId: selectedQuestion?.id,
                      language,
                      score,
                      results,
                      timestamp: new Date().toISOString(),
                      code: editorRef.current?.getValue(),
                    };

                    try {
                      sessionStorage.setItem(
                        `interview_session_${interviewSession}`,
                        JSON.stringify(sessionData)
                      );
                    } catch (error) {
                      console.warn("Could not store session data:", error);
                    }
                  }

                  // No auto-redirect to next problem
                  // Agent will handle question progression
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
