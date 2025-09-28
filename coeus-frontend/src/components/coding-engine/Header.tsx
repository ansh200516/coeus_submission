"use client";

import Timer from "./Timer";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  onTimeUp?: () => void;
  onSubmit?: () => void;
  onStart?: () => void;
}

const Header = ({ onTimeUp, onSubmit, onStart }: HeaderProps) => {
  return (
    <header className="bg-background/95 backdrop-blur-sm border-b border-border/30 sticky top-0 z-50 h-14">
      <div className="flex items-center justify-between px-6 h-full">
        {/* Logo */}
        <div className="flex items-center">
          <div className="w-12 h-12 bg-wheat rounded-md flex items-center justify-center">
            <img src="/assets/logo.svg" alt="Coeus Logo" className="w-9 h-9" />
          </div>
        </div>

        {/* Start & Submit Buttons - Center */}
        <div className="flex-1 flex items-center justify-center gap-4">
          <Button
            onClick={onStart}
            className="bg-green-600 hover:bg-green-700 text-white border-green-600 border-2 font-medium px-6"
          >
            Start Interview
          </Button>
          <Button
            onClick={onSubmit}
            className="bg-green-500/10 hover:bg-green-500 text-green-400 hover:text-black border-green-500/30 hover:border-green-500 border rounded-lg font-mono font-medium px-8 h-10 transition-all duration-200"
          >
            Submit Code
          </Button>
        </div>

        {/* Timer - Corner positioned */}
        <div className="flex items-center">
          <Timer onTimeUp={onTimeUp} />
        </div>
      </div>
    </header>
  );
};

export default Header;
