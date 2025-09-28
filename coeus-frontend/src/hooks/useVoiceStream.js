import { useState, useRef, useCallback, useEffect } from 'react';

const VOICE_STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  SPEAKING: 'speaking',
  PROCESSING: 'processing'
};

export function useVoiceStream() {
  const [voiceState, setVoiceState] = useState(VOICE_STATES.IDLE);
  const [amplitude, setAmplitude] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  
  const microphoneRef = useRef(null);
  const analyserRef = useRef(null);
  const audioContextRef = useRef(null);
  const websocketRef = useRef(null);
  const animationFrameRef = useRef(null);

  // Initialize microphone
  const initializeMicrophone = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        } 
      });
      
      microphoneRef.current = stream;
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      audioContextRef.current = audioContext;
      
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.8;
      analyserRef.current = analyser;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      setIsConnected(true);
      return stream;
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Failed to access microphone. Please check permissions.');
      throw err;
    }
  }, []);

  // Stop microphone
  const stopMicrophone = useCallback(() => {
    if (microphoneRef.current) {
      microphoneRef.current.getTracks().forEach(track => track.stop());
      microphoneRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    analyserRef.current = null;
    setIsConnected(false);
    setAmplitude(0);
    setVoiceState(VOICE_STATES.IDLE);
  }, []);

  // Connect to live voice stream (WebSocket)
  const connectToVoiceStream = useCallback(async (websocketUrl) => {
    try {
      setError(null);
      const stream = await initializeMicrophone();
      
      const websocket = new WebSocket(websocketUrl);
      websocketRef.current = websocket;
      
      websocket.onopen = () => {
        console.log('Connected to voice stream');
        setVoiceState(VOICE_STATES.LISTENING);
      };
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle different message types from voice stream
          switch (data.type) {
            case 'voice_start':
              setVoiceState(VOICE_STATES.LISTENING);
              break;
            case 'voice_end':
              setVoiceState(VOICE_STATES.PROCESSING);
              break;
            case 'response_start':
              setVoiceState(VOICE_STATES.SPEAKING);
              break;
            case 'response_end':
              setVoiceState(VOICE_STATES.IDLE);
              break;
            case 'amplitude':
              setAmplitude(data.value);
              break;
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (err) {
          console.error('Error parsing websocket message:', err);
        }
      };
      
      websocket.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('Connection to voice stream failed');
      };
      
      websocket.onclose = () => {
        console.log('Disconnected from voice stream');
        setVoiceState(VOICE_STATES.IDLE);
        websocketRef.current = null;
      };
      
      // Send audio data to websocket
      if (stream) {
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm;codecs=opus'
        });
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {
            websocket.send(event.data);
          }
        };
        
        mediaRecorder.start(100); // Send data every 100ms
      }
      
    } catch (err) {
      setError('Failed to connect to voice stream');
      console.error('Connection error:', err);
    }
  }, [initializeMicrophone]);

  // Disconnect from voice stream
  const disconnectFromVoiceStream = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    stopMicrophone();
  }, [stopMicrophone]);

  // Analyze audio for local amplitude detection
  const analyzeAudio = useCallback(() => {
    if (!analyserRef.current) return;
    
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    // Calculate RMS amplitude
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += (dataArray[i] / 255) ** 2;
    }
    const rms = Math.sqrt(sum / bufferLength);
    setAmplitude(prev => prev * 0.7 + rms * 0.3);
    
    // Simple voice activity detection
    const threshold = 0.02;
    if (rms > threshold && voiceState === VOICE_STATES.IDLE) {
      setVoiceState(VOICE_STATES.LISTENING);
    } else if (rms <= threshold && voiceState === VOICE_STATES.LISTENING) {
      setTimeout(() => setVoiceState(VOICE_STATES.IDLE), 2000);
    }
  }, [voiceState]);

  // Start local audio analysis loop
  useEffect(() => {
    if (isConnected && !websocketRef.current) {
      const analyzeLoop = () => {
        analyzeAudio();
        animationFrameRef.current = requestAnimationFrame(analyzeLoop);
      };
      animationFrameRef.current = requestAnimationFrame(analyzeLoop);
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isConnected, analyzeAudio]);

  // Manual voice state control
  const setVoiceStateManually = useCallback((newState) => {
    if (Object.values(VOICE_STATES).includes(newState)) {
      setVoiceState(newState);
    }
  }, []);

  // Simulate voice activity (for testing)
  const simulateVoiceActivity = useCallback((duration = 3000) => {
    setVoiceState(VOICE_STATES.LISTENING);
    setAmplitude(0.5);
    
    setTimeout(() => {
      setVoiceState(VOICE_STATES.PROCESSING);
      setAmplitude(0.1);
    }, duration * 0.7);
    
    setTimeout(() => {
      setVoiceState(VOICE_STATES.SPEAKING);
      setAmplitude(0.3);
    }, duration * 0.8);
    
    setTimeout(() => {
      setVoiceState(VOICE_STATES.IDLE);
      setAmplitude(0);
    }, duration);
  }, []);

  return {
    // State
    voiceState,
    amplitude,
    isConnected,
    error,
    
    // Controls
    initializeMicrophone,
    stopMicrophone,
    connectToVoiceStream,
    disconnectFromVoiceStream,
    setVoiceState: setVoiceStateManually,
    simulateVoiceActivity,
    
    // Constants
    VOICE_STATES
  };
}

export { VOICE_STATES };
