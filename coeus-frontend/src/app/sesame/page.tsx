'use client';

import { useState, useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { SimpleVoiceIndicator } from "@/components/SimpleVoiceIndicator";
import { VOICE_STATES } from "@/hooks/useVoiceStream";
import { Button } from "@/components/ui/button";
import { ppEditorialNew } from "@/lib/fonts";
import { Mic, MicOff, Square } from "lucide-react";

export default function VoiceIndicatorDemo() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [userName, setUserName] = useState("Guest");
  
  const [voiceState, setVoiceState] = useState(VOICE_STATES.IDLE);
  const [amplitude, setAmplitude] = useState(0);
  const [isListening, setIsListening] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  const audioStreamRef = useRef<MediaStream | null>(null);
  const micAudioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const appResponseTimerRef = useRef<NodeJS.Timeout | null>(null);

  let micProcessNode: (() => void) | null = null;

  useEffect(() => {
    const name = searchParams.get('name');
    if (name) setUserName(name);
  }, [searchParams]);

  const playAppResponse = () => {
    setVoiceState(VOICE_STATES.SPEAKING);

    const speakContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = speakContext.createOscillator();
    const gainNode = speakContext.createGain();
    const speakAnalyser = speakContext.createAnalyser();
    speakAnalyser.fftSize = 256;

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(220, speakContext.currentTime);
    gainNode.gain.setValueAtTime(0, speakContext.currentTime);

    oscillator.connect(gainNode);
    gainNode.connect(speakAnalyser);
    speakAnalyser.connect(speakContext.destination);
    oscillator.start();

    gainNode.gain.linearRampToValueAtTime(0.2, speakContext.currentTime + 0.5);
    gainNode.gain.linearRampToValueAtTime(0, speakContext.currentTime + 2.5);
    oscillator.stop(speakContext.currentTime + 3);

    let speakAnimationRef: number;
    const speakDataArray = new Uint8Array(speakAnalyser.frequencyBinCount);
    const processSpeakAudio = () => {
      speakAnalyser.getByteFrequencyData(speakDataArray);
      const avgAmplitude = speakDataArray.reduce((sum, value) => sum + value, 0) / speakDataArray.length;
      setAmplitude(Math.min(1, avgAmplitude / 128));
      speakAnimationRef = requestAnimationFrame(processSpeakAudio);
    };
    processSpeakAudio();

    oscillator.onended = () => {
      cancelAnimationFrame(speakAnimationRef);
      speakContext.close();
      setVoiceState(VOICE_STATES.IDLE);
      setAmplitude(0);
    };
  };

  const startListening = async () => {
    if (isListening) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      const context = new (window.AudioContext || (window as any).webkitAudioContext)();
      micAudioContextRef.current = context;
      const source = context.createMediaStreamSource(stream);
      const analyser = context.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.3;
      source.connect(analyser);
      analyserRef.current = analyser;
      setIsListening(true);
      setIsMuted(false);
      setVoiceState(VOICE_STATES.IDLE);
      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      micProcessNode = () => {
        if (!analyserRef.current || voiceState === VOICE_STATES.SPEAKING) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        const avgAmplitude = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
        const normalizedAmplitude = Math.min(1, avgAmplitude / 140);
        setAmplitude(normalizedAmplitude);

        const speakingThreshold = 0.05;
        if (normalizedAmplitude > speakingThreshold) {
          if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
          if (appResponseTimerRef.current) clearTimeout(appResponseTimerRef.current);
          silenceTimerRef.current = null;
          appResponseTimerRef.current = null;
          if (voiceState !== VOICE_STATES.LISTENING) setVoiceState(VOICE_STATES.LISTENING);
        } else {
          if (voiceState === VOICE_STATES.LISTENING) {
            if (!silenceTimerRef.current) {
              silenceTimerRef.current = setTimeout(() => {
                setVoiceState(VOICE_STATES.PROCESSING);
                appResponseTimerRef.current = setTimeout(playAppResponse, 1000);
              }, 1200);
            }
          }
        }
        animationFrameRef.current = requestAnimationFrame(micProcessNode as FrameRequestCallback);
      };
      micProcessNode();
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Microphone access is required.");
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    if (audioStreamRef.current) audioStreamRef.current.getTracks().forEach(track => track.stop());
    if (micAudioContextRef.current && micAudioContextRef.current.state !== 'closed') micAudioContextRef.current.close();
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    if (appResponseTimerRef.current) clearTimeout(appResponseTimerRef.current);
    
    audioStreamRef.current = null;
    animationFrameRef.current = null;
    silenceTimerRef.current = null;
    appResponseTimerRef.current = null;
    setIsListening(false);
    setVoiceState(VOICE_STATES.IDLE);
    setAmplitude(0);
  };

  const handleToggleMute = () => {
    if (!isListening || !audioStreamRef.current) return;
    audioStreamRef.current.getAudioTracks().forEach(track => {
      track.enabled = !track.enabled;
    });
    setIsMuted(prev => !prev);
  };

  useEffect(() => {
    startListening();
    return () => stopListening();
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      <div className="relative z-10 h-screen flex flex-col items-center justify-center">
        <div className="text-center -mt-20">
          <h1 className={`text-6xl font-extralight text-white mb-40 tracking-tight ${ppEditorialNew.className}`}>
            akira
          </h1>

          <div className="flex flex-col items-center mb-40">
            <div className="relative">
              <SimpleVoiceIndicator
                voiceState={voiceState}
                amplitude={amplitude}
                size={200}
              />
            </div>
          </div>

          <div className="flex gap-4 justify-center">
            <Button
              onClick={handleToggleMute}
              disabled={!isListening}
              className="rounded-full w-40 px-7 py-2.5 font-light text-sm bg-white/5 hover:bg-white/10 text-white/60 hover:text-white border border-white/10 hover:border-white/20 transition-all disabled:opacity-50"
              variant="ghost"
            >
              {isMuted ? <Mic className="w-4 h-4 mr-2" /> : <MicOff className="w-4 h-4 mr-2" />}
              {isMuted ? 'Unmute Mic' : 'Mute Mic'}
            </Button>
            
            <Button
              onClick={() => {
                stopListening();
                router.push('/end-call');
              }}
              className="rounded-full w-40 px-7 py-2.5 font-light text-sm bg-red-500/20 hover:bg-red-500/30 text-red-400 hover:text-red-300 border border-red-500/20 hover:border-red-500/30 transition-all"
              variant="ghost"
            >
              <Square className="w-4 h-4 mr-2" />
              End Call
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}