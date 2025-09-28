"use client";

import { useState } from "react";
import { useVoiceStream } from "@/hooks/useVoiceStream";
import { SimpleVoiceIndicator } from "@/components/SimpleVoiceIndicator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const { voiceState, amplitude, simulateVoiceActivity } = useVoiceStream();
  
  const handleSendMessage = () => {
    if (!inputText.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputText,
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    
    // Simulate AI response
    simulateVoiceActivity(3000);
    
    // Add AI response after a delay
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "This is a simulated response from the AI assistant.",
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    }, 2000);
  };
  
  return (
    <Card className="w-full max-w-2xl mx-auto p-4">
      <div className="flex items-center gap-3 mb-4">
        <SimpleVoiceIndicator
          voiceState={voiceState}
          amplitude={amplitude}
          size={24}
        />
        <h2 className="text-lg font-medium">Chat Assistant</h2>
      </div>
      
      <div className="h-[400px] overflow-y-auto mb-4 border rounded-md p-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            No messages yet
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`p-3 rounded-lg ${
                  message.role === "user"
                    ? "bg-blue-100 ml-auto max-w-[80%]"
                    : "bg-gray-100 max-w-[80%]"
                }`}
              >
                {message.content}
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="flex gap-2">
        <Input
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSendMessage();
            }
          }}
        />
        <Button onClick={handleSendMessage}>Send</Button>
      </div>
    </Card>
  );
}
