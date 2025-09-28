'use client';

import { VOICE_STATES } from "@/hooks/useVoiceStream";

interface SimpleVoiceIndicatorProps {
  voiceState?: string;
  amplitude?: number;
  size?: number;
  className?: string;
}

export function SimpleVoiceIndicator({
  voiceState = VOICE_STATES.IDLE,
  amplitude = 0,
  size = 200, // Default size from sesame page
  className = "",
}: SimpleVoiceIndicatorProps) {
  const isSpeaking = voiceState === VOICE_STATES.SPEAKING;
  const isListening = voiceState === VOICE_STATES.LISTENING;

  // Main circle's scale is driven by amplitude
  const mainCircleScale = 1 + amplitude * 0.25;
  
  // Main circle's opacity is also driven by amplitude for a "glow" effect
  const mainCircleOpacity = 0.3 + amplitude * 0.7;

  const rippleStyle: React.CSSProperties = {
    width: size,
    height: size,
    borderRadius: '50%',
    position: 'absolute',
    borderWidth: '1px',
    borderStyle: 'solid',
    animation: 'continuous-ripple 2s infinite cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  };

  return (
    <div
      className={`relative ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Continuous ripples for active states */}
      {(isListening || isSpeaking) && (
        <>
          <div style={rippleStyle} />
          <div style={{ ...rippleStyle, animationDelay: '1s' }} />
        </>
      )}
      
      {/* Main Circle */}
      <div
        className="absolute rounded-full border border-white/30 backdrop-blur-sm"
        style={{
          inset: 0,
          backgroundColor: `rgba(255, 255, 252, ${mainCircleOpacity})`,
          transform: `scale(${mainCircleScale})`,
          transition: "transform 120ms ease-out, background-color 200ms ease",
          boxShadow: voiceState !== VOICE_STATES.IDLE
            ? `0 0 ${size * 0.3}px rgba(255,255,255,0.4), inset 0 1px 0 rgba(255,255,255,0.3)` 
            : `inset 0 1px 0 rgba(255,255,255,0.2)`,
        }}
      />
      
      <style>{`
        @keyframes continuous-ripple {
          0% {
            transform: scale(0.8);
            opacity: 1;
            border-color: #e5e4e6;
          }
          30% {
            opacity: 0.5;
            border-color: #e5e4e6;
          }
          100% {
            transform: scale(2.5);
            opacity: 0;
            border-color: #e5e4e6;
          }
        }
      `}</style>
    </div>
  );
}