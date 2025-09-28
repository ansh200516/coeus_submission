'use client';

import { useState, useEffect } from 'react';

interface TimerProps {
  onTimeUp?: () => void;
}

const Timer = ({ onTimeUp }: TimerProps) => {
  const [time, setTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prevTime) => {
        const newTime = prevTime + 1;
        // Auto-submit after 30 minutes (1800 seconds)
        if (newTime >= 1800 && onTimeUp) {
          onTimeUp();
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [onTimeUp]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    return 'text-mahogany';  
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`text-lg font-mono font-bold ${getTimeColor()}`}>
        {formatTime(time)}
      </div>
    </div>
  );
};

export default Timer;
