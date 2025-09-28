"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { User, Linkedin, FileText, Send, ArrowRight, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { CustomFileInput } from "@/components/ui/custom-file-input";
import { ppEditorialNew } from "@/lib/fonts";
import Link from "next/link";
import { useInterviewStatus } from "@/hooks/useInterviewStatus";

import { motion } from "framer-motion";

// Dynamically import Galaxy to avoid SSR issues
const Galaxy = dynamic(
  () => import("@/components/Galaxy"),
  { ssr: false }
);

const LoadingComponent = ({ status }: { status?: any }) => {
  const getStatusIcon = () => {
    if (!status) return <Clock className="w-6 h-6" />;
    
    switch (status.processing_status) {
      case 'data_collection':
        return <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
        >
          <Clock className="w-6 h-6" />
        </motion.div>;
      case 'data_ready':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'interview_active':
        return <CheckCircle className="w-6 h-6 text-green-400" />;
      default:
        return <Clock className="w-6 h-6" />;
    }
  };

  const getStatusMessage = () => {
    if (!status) return "Submitting your application...";
    return status.message || "Processing your request...";
  };

  return (
    <div className="flex flex-col items-center justify-center text-white max-w-md mx-auto">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        {getStatusIcon()}
      </motion.div>
      
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="text-center"
      >
        <h2 className={`text-2xl font-light mb-3 ${ppEditorialNew.className}`}>
          Processing Your Application
        </h2>
        <p className="text-lg mb-4">{getStatusMessage()}</p>
        
        {status && (
          <div className="space-y-2 text-sm text-white/70">
            <div className="flex items-center justify-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                ['data_collection', 'data_ready', 'interview_active'].includes(status.processing_status) 
                  ? 'bg-green-400' 
                  : 'bg-white/30'
              }`} />
              <span>Data Collection</span>
            </div>
            <div className="flex items-center justify-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                ['data_ready', 'interview_active'].includes(status.processing_status) 
                  ? 'bg-green-400' 
                  : 'bg-white/30'
              }`} />
              <span>System Initialization</span>
            </div>
            <div className="flex items-center justify-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                status.processing_status === 'interview_active' 
                  ? 'bg-green-400' 
                  : 'bg-white/30'
              }`} />
              <span>Interview Ready</span>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export function InterviewForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [mounted, setMounted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    gender: '',
    linkedin: '',
    resume: null as File | null,
  });
  
  const { status, error, startPolling, stopPolling } = useInterviewStatus();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFormData((prev) => ({ ...prev, resume: file }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.resume) {
      alert("Please upload a resume.");
      return;
    }

    setIsLoading(true);

    const data = new FormData();
    data.append("name", formData.name);
    data.append("gender", formData.gender);
    data.append("linkedin_url", formData.linkedin);
    data.append("resume", formData.resume);

    try {
      const response = await fetch("http://localhost:8000/interview/start", {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start interview.");
      }

      const result = await response.json();
      console.log("Interview started:", result);
      
      // Start polling for status updates
      startPolling(result.task_id);

    } catch (error) {
      console.error("Error starting interview:", error);
      alert((error as Error).message);
      setIsLoading(false);
    }
  };

  // Handle errors from status polling
  useEffect(() => {
    if (error) {
      console.error("Interview status error:", error);
      alert(`Interview error: ${error}`);
      setIsLoading(false);
      stopPolling();
    }
  }, [error, stopPolling]);

  if (isLoading) {
    return (
      <div className="relative w-full min-h-screen overflow-hidden bg-black flex items-center justify-center">
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
        <div className="relative z-10">
          <LoadingComponent status={status} />
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-black">
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
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8">
        <div className={cn("w-full max-w-4xl mx-auto", className)} {...props}>
          {/* Coeus Branding */}
          <div className="text-center mb-12">
            <Link href="/" className={`text-4xl font-light text-white tracking-tight hover:text-white/80 transition-colors ${ppEditorialNew.className} flex items-center justify-center`}>
              <svg 
                width="100" 
                height="100" 
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

          <Card className="overflow-hidden p-0 backdrop-blur-xl bg-black/20 border-white/10">
            <CardContent className="grid p-0 lg:grid-cols-2">
              {/* Form Section */}
              <form className="p-12 lg:p-16" onSubmit={handleSubmit}>
                <div className="flex flex-col gap-8">
                  <div className="flex flex-col text-center">
                    <h1 className={`text-3xl font-light text-white mb-3 ${ppEditorialNew.className}`}>Begin Your Journey</h1>
                    <p className="text-white/70 text-balance leading-relaxed">
                      Submit your application to start the AI-powered interview process
                    </p>
                  </div>

                  <div className="space-y-6">
                    <div className="space-y-3">
                      <Label htmlFor="name" className="text-sm font-medium text-white/90 flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Full Name
                      </Label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="John Smith"
                        required
                        className="h-12 rounded-xl bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-white/30 focus:bg-white/10 transition-all"
                        onChange={handleInputChange}
                      />
                    </div>

                    <div className="space-y-3">
                      <Label htmlFor="gender" className="text-sm font-medium text-white/90 flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Gender
                      </Label>
                      <Input
                        id="gender"
                        type="text"
                        placeholder="Male/Female/Other"
                        required
                        className="h-12 rounded-xl bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-white/30 focus:bg-white/10 transition-all"
                        onChange={handleInputChange}
                      />
                    </div>

                    <div className="space-y-3">
                      <Label htmlFor="linkedin" className="text-sm font-medium text-white/90 flex items-center gap-2">
                        <Linkedin className="h-4 w-4" />
                        LinkedIn Profile
                      </Label>
                      <Input
                        id="linkedin"
                        type="url"
                        placeholder="https://linkedin.com/in/johnsmith"
                        required
                        className="h-12 rounded-xl bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-white/30 focus:bg-white/10 transition-all"
                        onChange={handleInputChange}
                      />
                    </div>

                    <div className="space-y-3">
                      <Label htmlFor="resume" className="text-sm font-medium text-white/90 flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        Resume
                        <span className="text-xs text-white/50 ml-2">(PDF only)</span>
                      </Label>
                      <div className="relative">
                        <CustomFileInput
                          id="resume"
                          accept=".pdf"
                          required
                          buttonText=""
                          onChange={handleFileChange}
                          className="h-12 rounded-xl bg-white/5 border-white/10 text-white hover:bg-white/10 transition-all flex items-center justify-center"
                        />
                      </div>
                    </div>

                    <div className="pt-4">
                      <Button type="submit" className="w-full h-12 rounded-xl bg-white text-black hover:bg-white/90 font-medium transition-all group">
                        <Send className="mr-2 h-4 w-4" />
                        Submit Application
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>

                    <div className="text-center pt-2">
                      <p className="text-xs text-white/50 leading-relaxed">
                        Our AI will review your application and guide you through a personalized interview process
                      </p>
                    </div>
                  </div>
                </div>
              </form>

              {/* Visual Section */}
              <div className="relative hidden lg:block bg-white/5 backdrop-blur-sm overflow-hidden">
                <div className="absolute inset-0">
                  <img 
                    src="/assets/ovo.jpg" 
                    alt="AI Interview Process"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-white/60 text-center text-xs mt-8 leading-relaxed">
            Your data is processed securely using enterprise-grade encryption and stored in compliance with{" "}
            <Link href="#" className="text-white/80 hover:text-white transition-colors">
              GDPR standards
            </Link>
            .
          </div>
        </div>
      </div>
    </div>
  )
}