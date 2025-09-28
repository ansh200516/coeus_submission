"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import { Brain, Zap, Database } from "lucide-react";
import { ppEditorialNew } from "@/lib/fonts";
import Link from "next/link";

// Dynamically import Galaxy to avoid SSR issues
const Galaxy = dynamic(
  () => import("@/components/Galaxy"),
  { ssr: false }
);

export default function AboutPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* Background Effect */}
      {mounted && (
        <div className="absolute inset-0 z-0 opacity-60">
          <Galaxy
            density={0.8}
            speed={0.5}
            hueShift={220}
            glowIntensity={0.2}
            saturation={0.3}
            twinkleIntensity={0.4}
            rotationSpeed={0.02}
            mouseRepulsion={true}
            repulsionStrength={1.2}
          />
        </div>
      )}

      {/* Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-between h-full p-8">
        {/* Navbar */}
        <div className="w-full max-w-4xl mx-auto mt-8">
          <div className="backdrop-blur-xl bg-black/20 border border-white/10 rounded-2xl px-8 py-4 flex items-center justify-between">
            <Link href="/" className={`text-white/95 font-medium text-lg flex items-center ${ppEditorialNew.className}`}>
              <svg 
                width="40" 
                height="30" 
                viewBox="0 0 400 300" 
                xmlns="http://www.w3.org/2000/svg"
                className="fill-current"
                aria-label="Coeus logo"
              >
                <g transform="translate(0.000000,300.000000) scale(0.100000,-0.100000)">
                  <path d="M510 2227 c0 -34 67 -144 122 -198 72 -72 205 -140 323 -165 44 -10
                  81 -18 83 -20 2 -1 -23 -29 -55 -61 -180 -180 -212 -460 -79 -688 15 -25 55
                  -73 88 -105 131 -128 316 -184 499 -150 86 16 214 84 283 151 33 32 61 58 62
                  56 1 -1 13 -25 27 -53 14 -27 50 -89 80 -137 l55 -88 55 88 c30 49 67 113 82
                  143 15 30 28 56 30 58 1 1 31 -26 66 -60 227 -222 571 -223 793 -2 220 221
                  220 569 0 790 l-61 62 81 16 c116 23 250 91 323 164 58 58 105 132 117 185 l7
                  28 -52 -26 c-112 -57 -313 -85 -594 -83 -105 1 -146 -3 -215 -21 -203 -54
                  -382 -189 -467 -355 l-20 -39 -142 0 -143 0 -36 64 c-55 99 -169 205 -277 261
                  -134 69 -231 91 -390 90 -281 -2 -482 26 -594 83 -37 18 -51 22 -51 12z m1004
                  -536 c63 -28 131 -94 163 -160 24 -48 28 -68 28 -141 0 -74 -4 -92 -29 -143
                  -101 -199 -368 -245 -524 -89 -21 21 -52 65 -67 97 -55 111 -33 258 53 356 32
                  37 115 87 166 100 48 13 161 2 210 -20z m1261 -10 c200 -99 243 -363 85 -521
                  -216 -216 -592 -37 -556 266 27 230 263 357 471 255z m-717 -198 c41 -25 53
                  -71 42 -158 -5 -42 -15 -96 -21 -118 -16 -60 -69 -187 -79 -187 -12 0 -58 104
                  -80 181 -10 38 -22 101 -26 139 -9 91 5 126 60 151 42 19 64 17 104 -8z" />
                </g>
              </svg>
            </Link>
            <div className="hidden sm:flex gap-8">
              <Link href="/about" className="text-white/70 hover:text-white text-sm transition-colors duration-200">About</Link>
              <Link href="/contact" className="text-white/70 hover:text-white text-sm transition-colors duration-200">Contact</Link>
            </div>
            <button className="sm:hidden text-white/70 hover:text-white transition-colors duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col items-center justify-center w-full px-8">
          <div className="mb-12 text-center">
            <h1 className={`text-5xl sm:text-6xl md:text-7xl font-light text-white tracking-tight mb-8 ${ppEditorialNew.className}`}>about</h1>
            <p className="text-xl sm:text-2xl text-white/85 font-light max-w-4xl mx-auto leading-relaxed">
              A revolutionary AI-powered mass interviewing platform built for modern recruitment.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-6">
            <Button asChild size="lg" className="bg-white text-black hover:bg-white/90 rounded-xl px-8 py-6 text-base font-medium transition-all duration-200">
              <Link href="/dashboard">View Demo</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10 rounded-xl px-8 py-6 text-base font-medium backdrop-blur-sm transition-all duration-200">
              <Link href="/contact">Get in Touch</Link>
            </Button>
          </div>
        </div>

        {/* Features Section */}
        <div className="font-sans text-sm text-white/75 grid grid-cols-1 md:grid-cols-3 w-full mt-auto">
          <div className="p-8 border-t border-white/10 bg-black/20 backdrop-blur-xl">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="h-5 w-5 text-white/80" />
              <h3 className="text-white font-medium tracking-wide">AI-Powered</h3>
            </div>
            <p className="leading-relaxed">Advanced AI algorithms conduct comprehensive interviews with intelligent assessment capabilities.</p>
          </div>
          
          <div className="p-8 border-t md:border-l border-white/10 bg-black/20 backdrop-blur-xl">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="h-5 w-5 text-white/80" />
              <h3 className="text-white font-medium tracking-wide">Scalable</h3>
            </div>
            <p className="leading-relaxed">Conduct hundreds of interviews simultaneously while maintaining consistent quality and evaluation standards.</p>
          </div>
          
          <div className="p-8 border-t md:border-l border-white/10 bg-black/20 backdrop-blur-xl">
            <div className="flex items-center gap-3 mb-4">
              <Database className="h-5 w-5 text-white/80" />
              <h3 className="text-white font-medium tracking-wide">Comprehensive</h3>
            </div>
            <p className="leading-relaxed">Covers technical, behavioral, and cultural assessments for complete candidate evaluation.</p>
          </div>
        </div>
      </div>
    </div>
  );
}