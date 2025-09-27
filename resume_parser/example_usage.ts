#!/usr/bin/env node

import { ResumeParser } from './parse_resume';
import * as path from 'path';

/**
 * Example usage of the resume parser
 * 
 * This script demonstrates how to use the ResumeParser class
 * to parse the provided resume PDF file.
 */

async function exampleUsage() {
  console.log('🚀 Resume Parser Example Usage');
  console.log('==============================\n');

  // Initialize the parser
  const parser = new ResumeParser();

  // Path to the resume PDF (adjust this path as needed)
  const resumePath = path.join(__dirname, '..', '2023CE11156_it.pdf');
  
  console.log(`📄 Attempting to parse resume: ${resumePath}\n`);

  try {
    // Parse the resume
    await parser.parseResume(resumePath);
    
    console.log('\n🎉 Resume parsing example completed successfully!');
    console.log('Check the logs directory for the generated JSON file.');
    
  } catch (error) {
    console.error('\n❌ Example failed:', error instanceof Error ? error.message : 'Unknown error');
    console.log('\n💡 Make sure:');
    console.log('   1. The resume PDF file exists at the specified path');
    console.log('   2. You have installed the required dependencies (npm install)');
    console.log('   3. The PDF is readable and not corrupted');
  }
}

// Instructions for different ways to run the parser
function printUsageInstructions() {
  console.log('\n📚 Usage Instructions:');
  console.log('======================');
  console.log('1. Run this example:');
  console.log('   npm run dev example_usage.ts');
  console.log('');
  console.log('2. Parse a specific file:');
  console.log('   npm run dev parse_resume.ts /path/to/your/resume.pdf');
  console.log('');
  console.log('3. After building (npm run build):');
  console.log('   node dist/parse_resume.js /path/to/your/resume.pdf');
  console.log('');
  console.log('4. Using the parse script:');
  console.log('   npm run parse /path/to/your/resume.pdf');
}

if (require.main === module) {
  exampleUsage()
    .then(() => {
      printUsageInstructions();
    })
    .catch(console.error);
}
