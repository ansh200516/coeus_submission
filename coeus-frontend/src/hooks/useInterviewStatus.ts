/**
 * Custom hook for polling interview status and handling navigation
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface InterviewStatus {
  task_id: string;
  status: string;
  processing_status: string;
  message: string;
  ready_for_interview: boolean;
  redirect_url?: string;
}

interface UseInterviewStatusReturn {
  status: InterviewStatus | null;
  isLoading: boolean;
  error: string | null;
  startPolling: (taskId: string) => void;
  stopPolling: () => void;
}

export const useInterviewStatus = (): UseInterviewStatusReturn => {
  const [status, setStatus] = useState<InterviewStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);
  const [pollCount, setPollCount] = useState(0);
  
  const router = useRouter();

  const fetchStatus = useCallback(async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/interview/status/${id}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: InterviewStatus = await response.json();
      setStatus(data);
      setError(null);
      
      // Check if ready for interview and should redirect
      if (data.ready_for_interview && data.redirect_url) {
        console.log('Interview ready, redirecting to:', data.redirect_url);
        stopPolling();
        router.push(data.redirect_url);
      }
      
      // Stop polling if failed
      if (data.status === 'failed') {
        stopPolling();
        setError(data.message);
      }
      
    } catch (err) {
      console.error('Error fetching interview status:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    }
  }, [router]);

  const startPolling = useCallback((id: string) => {
    console.log('Starting status polling for task:', id);
    setTaskId(id);
    setIsLoading(true);
    setError(null);
    setPollCount(0);
    
    // Initial fetch
    fetchStatus(id);
    
    // Set up polling interval (every 4 seconds - reasonable balance)
    const interval = setInterval(() => {
      fetchStatus(id);
      setPollCount(prev => prev + 1);
    }, 4000);
    
    setPollInterval(interval);
  }, [fetchStatus]);

  const stopPolling = useCallback(() => {
    console.log('Stopping status polling');
    if (pollInterval) {
      clearInterval(pollInterval);
      setPollInterval(null);
    }
    setIsLoading(false);
  }, [pollInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [pollInterval]);

  return {
    status,
    isLoading,
    error,
    startPolling,
    stopPolling
  };
};
