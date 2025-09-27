#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';

/**
 * Section Viewer Tool
 * 
 * This script reads a parsed resume JSON file and displays
 * all sections and their content in a structured format.
 */

interface ParsedResumeLog {
  timestamp: string;
  filename: string;
  sections: Record<string, string[]>;
  metadata: {
    parserVersion: string;
    processingTime: number;
    status: string;
    errorMessage?: string;
  };
}

function viewSections(jsonFilePath: string): void {
  console.log('📋 Resume Section Viewer');
  console.log('========================\n');

  // Read the JSON file
  const jsonData = fs.readFileSync(jsonFilePath, 'utf8');
  const resumeData: ParsedResumeLog = JSON.parse(jsonData);

  console.log(`📄 File: ${resumeData.filename}`);
  console.log(`🕒 Parsed: ${new Date(resumeData.timestamp).toLocaleString()}`);
  console.log(`⚡ Processing Time: ${resumeData.metadata.processingTime}ms`);
  console.log(`✅ Status: ${resumeData.metadata.status}\n`);

  const sections = resumeData.sections;
  
  if (!sections || Object.keys(sections).length === 0) {
    console.log('❌ No sections found in the resume data.');
    return;
  }

  console.log(`📑 Found ${Object.keys(sections).length} sections:\n`);

  // Display each section with its content
  Object.entries(sections).forEach(([sectionName, content], index) => {
    console.log(`${index + 1}. 📋 ${sectionName.toUpperCase()}`);
    console.log('   ' + '='.repeat(sectionName.length + 8));
    
    if (content.length === 0) {
      console.log('   (No content)');
    } else {
      content.forEach((item, itemIndex) => {
        const prefix = itemIndex === 0 ? '   📌 ' : '      ';
        console.log(`${prefix}${item}`);
      });
    }
    console.log(); // Empty line between sections
  });

  // Show sections summary
  console.log('📊 Sections Summary:');
  console.log('====================');
  Object.entries(sections).forEach(([sectionName, content]) => {
    console.log(`📋 ${sectionName}: ${content.length} items`);
  });
}

// Main execution
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('❓ Usage: npx ts-node view_sections.ts <path-to-resume-json>');
    console.log('   Example: npx ts-node view_sections.ts ../logs/resume_example.json');
    
    // Try to find the latest resume file
    const logsDir = path.join(__dirname, '..', 'logs');
    if (fs.existsSync(logsDir)) {
      const files = fs.readdirSync(logsDir)
        .filter(f => f.startsWith('resume_') && f.endsWith('.json'))
        .sort()
        .reverse();
      
      if (files.length > 0) {
        console.log(`\n💡 Found latest resume file: ${files[0]}`);
        console.log(`   Running: npx ts-node view_sections.ts ../logs/${files[0]}`);
        viewSections(path.join(logsDir, files[0]));
        return;
      }
    }
    process.exit(1);
  }

  const jsonFilePath = args[0];
  
  if (!fs.existsSync(jsonFilePath)) {
    console.error(`❌ File not found: ${jsonFilePath}`);
    process.exit(1);
  }

  try {
    viewSections(jsonFilePath);
  } catch (error) {
    console.error('❌ Error reading or parsing JSON file:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}
