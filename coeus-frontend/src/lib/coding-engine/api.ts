import axios from 'axios';
import { LANGUAGE_VERSIONS } from './constants';

const API = axios.create({
  baseURL: 'https://emkc.org/api/v2/piston',
  timeout: 30000, // 30 second timeout for interview scenarios
});

export interface ExecuteCodeResponse {
  run: {
    stdout: string;
    stderr: string;
    output: string;
    code: number;
  };
}

export const executeCode = async (
  language: string,
  sourceCode: string,
  input: string = ''
): Promise<ExecuteCodeResponse> => {
  try {
    const response = await API.post('/execute', {
      language: language,
      version: LANGUAGE_VERSIONS[language as keyof typeof LANGUAGE_VERSIONS],
      files: [
        {
          content: sourceCode,
        },
      ],
      stdin: input,
    });
    return response.data;
  } catch (error: any) {
    // Enhanced error handling for interview scenarios
    console.error('Code execution error:', error);
    throw new Error(
      error.response?.data?.message ||
      error.message ||
      'Failed to execute code. Please check your internet connection and try again.'
    );
  }
};
