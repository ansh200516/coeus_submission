"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Mail, Send, ArrowLeft } from "lucide-react";
import { ppEditorialNew } from "@/lib/fonts";
import Link from "next/link";

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Contact form submitted:", formData);
    // Handle form submission logic here
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-black">
      {/* Content Container */}
      <div className="relative z-10 h-screen flex flex-col">
        {/* Minimal Header */}
        <div className="flex items-center justify-between px-10 py-7">
          <Link
            href="/"
            className="flex items-center gap-2 text-white/50 hover:text-white/70 transition-colors group"
          >
            <ArrowLeft className="h-5 w-5 group-hover:-translate-x-0.5 transition-transform" />
            <span className="text-sm">Back</span>
          </Link>
          <Link
            href="/"
            className={`text-white/60 hover:text-white font-light text-lg tracking-tight transition-colors ${ppEditorialNew.className} flex items-center`}
          >
            <svg 
              width="38" 
              height="28" 
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
        </div>

        {/* Main Content - Centered */}
        <div className="flex-1 flex items-center justify-center px-10">
          <div className="w-full max-w-xl">
            {/* Clean Title */}
            <div className="text-center mb-14">
              <h1 className={`text-6xl font-extralight text-white mb-5 tracking-tight ${ppEditorialNew.className}`}>
                contact
              </h1>
              <p className="text-base text-white/40 font-light tracking-wide">
                get in touch
              </p>
            </div>

            {/* Clean Contact Form */}
            <Card className="backdrop-blur-sm bg-white/5 border-white/10 p-14">
              <form onSubmit={handleSubmit} className="space-y-8">
                <div className="space-y-6">
                  <div className="space-y-3">
                    <Label htmlFor="name" className="text-sm font-light text-white/70 tracking-wide">
                      name
                    </Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="your name"
                      required
                      className="h-12 rounded-lg bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-white/30 focus:bg-white/8 transition-all text-sm"
                      value={formData.name}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="email" className="text-sm font-light text-white/70 tracking-wide">
                      email
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@company.com"
                      required
                      className="h-12 rounded-lg bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-white/30 focus:bg-white/8 transition-all text-sm"
                      value={formData.email}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="message" className="text-sm font-light text-white/70 tracking-wide">
                      message
                    </Label>
                    <Textarea
                      id="message"
                      placeholder="tell us how we can help..."
                      required
                      className="min-h-[120px] rounded-lg bg-white/5 border-white/10 text-white placeholder:text-white/30 focus:border-white/30 focus:bg-white/8 transition-all resize-none text-sm"
                      value={formData.message}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 rounded-lg bg-white/10 hover:bg-white/15 text-white border border-white/20 hover:border-white/30 font-light text-sm transition-all group"
                >
                  <Send className="w-4 h-4 mr-2" />
                  send message
                  <ArrowLeft className="w-4 h-4 ml-2 group-hover:translate-x-0.5 transition-transform rotate-180" />
                </Button>
              </form>
            </Card>

            {/* Minimal Contact Info */}
            <div className="mt-14 text-center space-y-4">
              <div className="flex items-center justify-center gap-3 text-white/40">
                <Mail className="h-4 w-4" />
                <span className="text-sm font-light tracking-wide">hello@coeus.ai</span>
              </div>
              <p className="text-xs text-white/25 tracking-widest">
                enterprise ai interviewing platform
              </p>
            </div>
          </div>
        </div>

        {/* Minimal Footer */}
        <div className="px-10 py-7 text-center">
          <p className="text-white/20 text-xs tracking-widest">
            silicon valley • california
          </p>
        </div>
      </div>
    </div>
  );
}