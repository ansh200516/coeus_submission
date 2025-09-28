'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ppEditorialNew } from '@/lib/fonts';
import Galaxy from '@/components/Galaxy';

export default function EndCallPage() {
  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      <Galaxy className="absolute inset-0 z-0" />
      <div className="relative z-10 h-full flex flex-col items-center justify-center text-center px-10">
        <h1 className={`text-5xl font-extralight text-white mb-8 tracking-tight ${ppEditorialNew.className}`}>
          Your call has ended.
        </h1>
        <p className="text-white/60 mb-12">Thank you for using our service.</p>
        <Link href="/">
          <Button
            className="rounded-full px-8 py-3 font-light text-sm bg-white/10 hover:bg-white/20 text-white/80 hover:text-white border border-white/20 hover:border-white/30 transition-all"
            variant="ghost"
          >
            Return to Home
          </Button>
        </Link>
      </div>
    </div>
  );
}
