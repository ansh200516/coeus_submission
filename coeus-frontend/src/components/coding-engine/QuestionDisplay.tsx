'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Question } from '@/lib/coding-engine/types';
interface QuestionDisplayProps {
  question: Question | null;
}

const QuestionDisplay = ({ question }: QuestionDisplayProps) => {
  if (!question) {
    return (
      <Card>
        <CardContent className="p-4">
          <p className="text-muted-foreground">Select a question to get started</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full bg-card border-border rounded-none">
      <CardContent className="p-0 h-full">
        <ScrollArea className="h-full">
          <div className="p-6 space-y-6">
            {/* Description */}
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <div className="text-foreground leading-relaxed font-mono">
                {question.description.replace(/\n\n/g, ' ')}
              </div>
            </div>

            {/* Examples */}
            {question.examples && question.examples.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">
                  Examples
                </h3>
                <div className="space-y-4">
                  {question.examples.map((example, index) => (
                    <div key={index} className="bg-muted/30 p-4 border border-border/50 rounded-none">
                      <div className="text-sm font-medium text-foreground mb-3 flex items-center">
                        <span className="bg-primary text-primary-foreground w-5 h-5 flex items-center justify-center text-xs mr-2 font-mono">
                          {index + 1}
                        </span>
                        Example {index + 1}
                      </div>
                      <div className="space-y-3 text-sm">
                        <div>
                          <span className="font-medium text-blue-400">Input:</span>
                          <div className="mt-1 p-2 bg-background border rounded-none font-mono text-xs text-foreground">
                            {example.input}
                          </div>
                        </div>
                        <div>
                          <span className="font-medium text-green-400">Output:</span>
                          <div className="mt-1 p-2 bg-background border rounded-none font-mono text-xs text-foreground">
                            {example.output}
                          </div>
                        </div>
                        {example.explanation && (
                          <div>
                            <span className="font-medium text-purple-400">Explanation:</span>
                            <div className="mt-1 text-muted-foreground text-xs leading-relaxed font-mono">
                              {example.explanation}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Constraints */}
            {question.constraints && question.constraints.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground border-b border-border pb-2">
                  Constraints
                </h3>
                <ul className="space-y-2">
                  {question.constraints.map((constraint, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-muted-foreground mr-2">•</span>
                      <code className="bg-muted px-2 py-1 rounded-none text-xs text-foreground font-mono">
                        {constraint}
                      </code>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default QuestionDisplay;
