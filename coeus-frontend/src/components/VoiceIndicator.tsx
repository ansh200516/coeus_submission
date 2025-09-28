"use client";

import { useEffect, useRef, useState } from "react";
import { VOICE_STATES } from "@/hooks/useVoiceStream";

interface VoiceIndicatorProps {
  voiceState?: string;
  amplitude?: number;
  size?: number;
  colors?: {
    idle: string;
    listening: string;
    speaking: string;
    processing: string;
  };
}

export function VoiceIndicator({
  voiceState = VOICE_STATES.IDLE,
  amplitude = 0,
  size = 64,
  colors = {
    idle: "#3b82f6",
    listening: "#10b981",
    speaking: "#8b5cf6",
    processing: "#f59e0b",
  },
}: VoiceIndicatorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [ripples, setRipples] = useState<{ id: number; scale: number; opacity: number }[]>([]);
  const rippleIdRef = useRef(0);
  
  // Calculate the current color based on voice state
  const currentColor = colors[voiceState as keyof typeof colors] || colors.idle;
  
  // Calculate size based on amplitude and voice state
  const baseSize = size;
  const minScale = 0.9;
  const maxScale = 1.2;
  
  // Calculate actual scale based on voice state and amplitude
  let actualScale = minScale + (maxScale - minScale) * (amplitude || 0);
  
  // When speaking, make the pulsation more pronounced
  if (voiceState === VOICE_STATES.SPEAKING) {
    actualScale = minScale + (maxScale - minScale) * (0.7 + 0.3 * (amplitude || 0));
  }
  
  // Create ripple effect when speaking
  useEffect(() => {
    if (voiceState !== VOICE_STATES.SPEAKING) return;
    
    const rippleInterval = setInterval(() => {
      const newRipple = {
        id: rippleIdRef.current++,
        scale: 1,
        opacity: 0.6,
      };
      
      setRipples((prev) => [...prev, newRipple]);
    }, 1000);
    
    return () => clearInterval(rippleInterval);
  }, [voiceState]);
  
  // Animate ripples
  useEffect(() => {
    if (ripples.length === 0) return;
    
    const animationFrame = requestAnimationFrame(() => {
      setRipples((prev) => 
        prev
          .map((ripple) => ({
            ...ripple,
            scale: ripple.scale + 0.03,
            opacity: ripple.opacity - 0.01,
          }))
          .filter((ripple) => ripple.opacity > 0)
      );
    });
    
    return () => cancelAnimationFrame(animationFrame);
  }, [ripples]);
  
  return (
    <div 
      ref={containerRef}
      className="relative flex items-center justify-center"
      style={{
        width: `${baseSize}px`,
        height: `${baseSize}px`,
      }}
    >
      {/* Ripples */}
      {ripples.map((ripple) => (
        <div
          key={ripple.id}
          className="absolute rounded-full"
          style={{
            width: `${baseSize}px`,
            height: `${baseSize}px`,
            backgroundColor: currentColor,
            transform: `scale(${ripple.scale})`,
            opacity: ripple.opacity,
            transition: "transform 100ms linear, opacity 100ms linear",
          }}
        />
      ))}
      
      {/* Main circle */}
      <div
        className="rounded-full"
        style={{
          width: `${baseSize}px`,
          height: `${baseSize}px`,
          backgroundColor: currentColor,
          transform: `scale(${actualScale})`,
          transition: "transform 150ms ease-out, background-color 300ms ease",
        }}
      />
    </div>
  );
}
