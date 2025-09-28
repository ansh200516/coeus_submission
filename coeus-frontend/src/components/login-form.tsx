"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Mail, Lock, Apple, Chrome, Facebook, ArrowRight, AlertCircle } from "lucide-react"
import { ppEditorialNew } from "@/lib/fonts";
import Link from "next/link";

// Dynamically import Galaxy to avoid SSR issues
const Galaxy = dynamic(
  () => import("@/components/Galaxy"),
  { ssr: false }
);

// Dummy credentials for authentication
const DUMMY_CREDENTIALS = {
  email: "admin@coeus.ai",
  password: "admin123"
};

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [mounted, setMounted] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Check dummy credentials
    if (email === DUMMY_CREDENTIALS.email && password === DUMMY_CREDENTIALS.password) {
      // Successful login - redirect to dashboard
      router.push("/dashboard");
    } else {
      // Invalid credentials
      setError("Invalid email or password. Use admin@coeus.ai / admin123");
    }

    setIsLoading(false);
  };

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
          <div className="text-center mb-6">
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
              <form className="p-8 lg:p-10" onSubmit={handleSubmit}>
                <div className="flex flex-col gap-5">
                  <div className="flex flex-col text-center">
                    <h1 className={`text-2xl font-light text-white mb-2 ${ppEditorialNew.className}`}>Welcome back</h1>
                    <p className="text-white/70 text-balance text-sm">
                      Access your Coeus dashboard
                    </p>
                  </div>

                  {/* Error Display */}
                  {error && (
                    <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                      <AlertCircle className="h-4 w-4 flex-shrink-0" />
                      <span>{error}</span>
                    </div>
                  )}

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-sm font-medium text-white/90 flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        Email Address
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="admin@coeus.ai"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-10 rounded-xl bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-white/30 focus:bg-white/10 transition-all disabled:opacity-50"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="password" className="text-sm font-medium text-white/90 flex items-center gap-2">
                          <Lock className="h-4 w-4" />
                          Password
                        </Label>
                        <Link
                          href="#"
                          className="text-sm text-white/60 hover:text-white/80 transition-colors"
                        >
                          Forgot password?
                        </Link>
                      </div>
                      <Input 
                        id="password" 
                        type="password"
                        placeholder="admin123"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        disabled={isLoading}
                        className="h-10 rounded-xl bg-white/5 border-white/10 text-white placeholder:text-white/40 focus:border-white/30 focus:bg-white/10 transition-all disabled:opacity-50" 
                      />
                    </div>

                    <Button 
                      type="submit" 
                      disabled={isLoading}
                      className="w-full h-10 rounded-xl bg-white text-black hover:bg-white/90 font-medium transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? "Signing In..." : "Sign In"}
                      {!isLoading && <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />}
                    </Button>
                  </div>

                  <div className="relative text-center text-sm">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-white/10" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase tracking-wide">
                      <span className="bg-black px-4 text-white/60">
                        Or continue with
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <Button variant="outline" type="button" className="h-12 rounded-xl border-white/10 bg-white/5 hover:bg-white/10 transition-all">
                      <Apple className="h-5 w-5 text-white" />
                      <span className="sr-only">Continue with Apple</span>
                    </Button>
                    <Button variant="outline" type="button" className="h-12 rounded-xl border-white/10 bg-white/5 hover:bg-white/10 transition-all">
                      <Chrome className="h-5 w-5 text-white" />
                      <span className="sr-only">Continue with Google</span>
                    </Button>
                    <Button variant="outline" type="button" className="h-12 rounded-xl border-white/10 bg-white/5 hover:bg-white/10 transition-all">
                      <Facebook className="h-5 w-5 text-white" />
                      <span className="sr-only">Continue with Facebook</span>
                    </Button>
                  </div>

                  <div className="text-center text-sm">
                    <span className="text-white/60">Don't have an account?</span>{" "}
                    <Link href="#" className="text-white hover:text-white/80 font-medium transition-colors">
                      Create account
                    </Link>
                  </div>
                </div>
              </form>

              {/* Visual Section */}
              <div className="relative hidden lg:block bg-white/5 backdrop-blur-sm overflow-hidden">
                <div className="absolute inset-0">
                  <img 
                    src="/assets/ovo.jpg" 
                    alt="Coeus AI"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-white/60 text-center text-xs mt-8 leading-relaxed">
            By continuing, you agree to our{" "}
            <Link href="#" className="text-white/80 hover:text-white transition-colors">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#" className="text-white/80 hover:text-white transition-colors">
              Privacy Policy
            </Link>
            .
          </div>
        </div>
      </div>
    </div>
  )
}