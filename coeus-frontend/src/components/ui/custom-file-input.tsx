'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface CustomFileInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  buttonText?: string;
}

export function CustomFileInput({ className, buttonText = 'Choose file', ...props }: CustomFileInputProps) {
  const [fileName, setFileName] = useState('');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setFileName(file ? file.name : '');
    if (props.onChange) {
      props.onChange(event);
    }
  };

  return (
    <div className={cn('grid w-full items-center gap-1.5', className)}>
      <label className="flex items-center justify-center w-full h-12 rounded-xl border border-white/10 bg-white/5 text-sm font-medium text-white cursor-pointer hover:bg-white/10 transition-all">
        <div className="flex items-center w-full h-full">
          <div className="flex items-center justify-center w-1/3 h-full px-4">
            {buttonText}
          </div>
          <div className="flex items-center justify-start flex-1 h-full px-4 text-left">
            <span className={fileName ? 'text-white/80' : 'text-white/40'}>
              {fileName || 'No file chosen'}
            </span>
          </div>
        </div>
        <input {...props} type="file" className="sr-only" onChange={handleFileChange} />
      </label>
    </div>
  );
}