"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Menu, X } from "lucide-react";
import { ppEditorialNew } from "@/lib/fonts";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  className?: string;
}

export function SiteNavbar({ className = "" }: NavbarProps) {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { href: "/about", label: "About" },
    { href: "/contact", label: "Contact" },
  ];

  return (
    <div className={`w-full max-w-6xl mx-auto mt-8 px-8 ${className}`}>
      <div className="backdrop-blur-xl bg-black/20 border border-white/10 rounded-2xl px-8 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link 
          href="/" 
          className={`text-white/95 font-light text-xl tracking-tight hover:text-white transition-colors ${ppEditorialNew.className} flex items-center`}
        >
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

        {/* Desktop Navigation */}
        <div className="hidden md:flex gap-8">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-white/70 hover:text-white text-sm font-medium transition-colors duration-200"
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* CTA Buttons */}
        <div className="hidden md:flex items-center gap-4">
          <Link href="/login">
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-white/70 hover:text-white hover:bg-white/10 transition-all"
            >
              Sign In
            </Button>
          </Link>
          <Link href="/interview">
            <Button 
              size="sm" 
              className="bg-white text-black hover:bg-white/90 rounded-xl px-6 transition-all"
            >
              Get Started
            </Button>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden text-white/70 hover:text-white transition-colors duration-200"
          aria-label="Toggle menu"
        >
          {isOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="md:hidden mt-4 backdrop-blur-xl bg-black/20 border border-white/10 rounded-2xl p-6">
          <div className="flex flex-col space-y-4">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-white/70 hover:text-white text-sm font-medium transition-colors duration-200 py-2"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <div className="flex flex-col gap-3 pt-4 border-t border-white/10">
              <Link href="/login" onClick={() => setIsOpen(false)}>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="w-full text-white/70 hover:text-white hover:bg-white/10 transition-all"
                >
                  Sign In
                </Button>
              </Link>
              <Link href="/interview" onClick={() => setIsOpen(false)}>
                <Button 
                  size="sm" 
                  className="w-full bg-white text-black hover:bg-white/90 rounded-xl transition-all"
                >
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
