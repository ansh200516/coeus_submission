export interface Question {
  id: number;
  title: string;
  difficulty: string;
  problemType?: string;
  level?: number;
  description: string;
  examples: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
  constraints: string[];
  testCases: Array<{
    input: string;
    expectedOutput: string;
  }>;
}
