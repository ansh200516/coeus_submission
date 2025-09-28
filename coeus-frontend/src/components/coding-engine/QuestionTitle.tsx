'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Question } from '@/lib/coding-engine/types';

interface QuestionTitleProps {
  question: Question | null;
}

const QuestionTitle = ({ question }: QuestionTitleProps) => {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'hard':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  if (!question) {
    return (
      <Card className="rounded-none">
        <CardContent className="p-4">
          <p className="text-muted-foreground text-lg font-mono">
            Waiting for interviewer to assign problem...
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="rounded-none">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold font-mono">Problem:</h2>
          <Badge variant="secondary" className={`${getDifficultyColor(question.difficulty)} rounded-none font-mono`}>
            {question.difficulty}
          </Badge>
        </div>
        <div className="text-xl font-semibold text-foreground font-mono">
          {question.id}. {question.title}
        </div>
      </CardContent>
    </Card>
  );
};

export default QuestionTitle;
