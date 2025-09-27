#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';

// Import pdfjs directly since we need to work around the Next.js module structure
import * as pdfjs from 'pdfjs-dist';
// @ts-ignore
import pdfjsWorker from 'pdfjs-dist/build/pdf.worker.entry';
pdfjs.GlobalWorkerOptions.workerSrc = pdfjsWorker;

// Define types locally since the open-resume types are in Next.js context
interface ResumeProfile {
  name: string;
  email: string;
  phone: string;
  url: string;
  summary: string;
  location: string;
}

interface ResumeWorkExperience {
  company: string;
  jobTitle: string;
  date: string;
  descriptions: string[];
}

interface ResumeEducation {
  school: string;
  degree: string;
  date: string;
  gpa: string;
  descriptions: string[];
}

interface ResumeProject {
  project: string;
  date: string;
  descriptions: string[];
}

interface FeaturedSkill {
  skill: string;
  rating: number;
}

interface ResumeSkills {
  featuredSkills: FeaturedSkill[];
  descriptions: string[];
}

interface ResumeCustom {
  descriptions: string[];
  sections?: Record<string, string[]>;
}

interface Resume {
  profile: ResumeProfile;
  workExperiences: ResumeWorkExperience[];
  educations: ResumeEducation[];
  projects: ResumeProject[];
  skills: ResumeSkills;
  custom: ResumeCustom;
}

/**
 * Resume Parser Tool using PDF.js and pattern matching
 * 
 * This script parses a resume PDF using pdfjs-dist for text extraction
 * and saves the extracted data as JSON in the logs directory.
 */

interface TextItem {
  text: string;
  x: number;
  y: number;
  width: number;
  height: number;
  fontName: string;
  hasEOL: boolean;
}

interface ParsedResumeLog {
  timestamp: string;
  filename: string;
  sections: Record<string, string[]>;
  metadata: {
    parserVersion: string;
    processingTime: number;
    status: 'success' | 'error';
    errorMessage?: string;
  };
}

class ResumeParser {
  private logsDir: string;
  
  constructor() {
    // Set up logs directory path relative to the script location
    this.logsDir = path.join(__dirname, '..', 'logs');
    this.ensureLogsDirectoryExists();
  }

  private ensureLogsDirectoryExists(): void {
    if (!fs.existsSync(this.logsDir)) {
      fs.mkdirSync(this.logsDir, { recursive: true });
      console.log(`Created logs directory: ${this.logsDir}`);
    }
  }

  private generateLogFilename(originalFilename: string): string {
    const timestamp = new Date().toISOString()
      .replace(/[-:]/g, '')
      .replace(/\.\d{3}Z$/, '');
    const baseName = path.basename(originalFilename, path.extname(originalFilename));
    return `resume_${baseName}_${timestamp}.json`;
  }

  private async saveToLogFile(data: any, filename: string): Promise<void> {
    const logFilePath = path.join(this.logsDir, filename);
    
    try {
      const jsonData = JSON.stringify(data, null, 2);
      fs.writeFileSync(logFilePath, jsonData, 'utf8');
      console.log(`✅ Resume data saved to: ${logFilePath}`);
    } catch (error) {
      console.error('❌ Error saving log file:', error);
      throw error;
    }
  }

  private async readPdf(filePath: string): Promise<TextItem[]> {
    const fileBuffer = fs.readFileSync(filePath);
    const uint8Array = new Uint8Array(fileBuffer);
    const pdfDoc = await pdfjs.getDocument({ data: uint8Array }).promise;
    let textItems: TextItem[] = [];

    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
      const page = await pdfDoc.getPage(pageNum);
      const textContent = await page.getTextContent();
      
      // Wait for font data to be loaded
      await page.getOperatorList();
      const commonObjs = page.commonObjs;

      const pageTextItems = textContent.items.map((item: any) => {
        const { str: text, transform, fontName: pdfFontName, width, height, hasEOL } = item;
        
        // Extract x, y position from transform
        const x = transform[4];
        const y = transform[5];

        // Get font name
        let fontName = pdfFontName;
        try {
          const fontObj = commonObjs.get(pdfFontName);
          fontName = fontObj?.name || pdfFontName;
        } catch (e) {
          // Use original font name if can't resolve
        }

        return {
          text: text.replace(/-­‐/g, "-"), // Fix hyphen encoding
          x,
          y,
          width: width || 0,
          height: height || 0,
          fontName,
          hasEOL: hasEOL || false
        };
      });

      textItems.push(...pageTextItems);
    }

    // Filter out empty items
    return textItems.filter(item => item.text.trim().length > 0);
  }

  private parseTextItems(textItems: TextItem[]): Resume {
    // Sort text items by Y position (top to bottom) to maintain reading order
    const sortedItems = textItems.sort((a, b) => b.y - a.y);
    
    // Group text into sections based on the resume structure
    const sections = this.extractSections(sortedItems);
    
    // Extract profile information
    const profile = this.extractProfileFromSections(sections, sortedItems);
    const workExperiences = this.extractWorkExperienceFromSections(sections);
    const educations = this.extractEducationFromSections(sections);
    const projects = this.extractProjectsFromSections(sections);
    const skills = this.extractSkillsFromSections(sections);

    return {
      profile,
      workExperiences,
      educations,
      projects,
      skills,
      custom: { 
        descriptions: [],
        sections: sections // Store all sections for reference
      }
    };
  }

  private extractSections(sortedItems: TextItem[]): Record<string, string[]> {
    const sections: Record<string, string[]> = {};
    let currentSection = 'HEADER';
    let currentContent: string[] = [];

    // Define section headers to look for
    const sectionHeaders = [
      'ACADEMIC DETAILS',
      'SCHOLASTIC ACHIEVEMENTS', 
      'INTERNSHIPS',
      'PROJECTS',
      'TECHNICAL SKILLS',
      'IIT COURSE',
      'COURSES DONE',
      'QUALIFYING EXAM',
      'POSITIONS OF RESPONSIBILITY'
    ];

    for (const item of sortedItems) {
      const text = item.text.trim();
      
      // Check if this text is a section header
      const matchedSection = sectionHeaders.find(header => 
        text.toUpperCase().includes(header) || header.includes(text.toUpperCase())
      );

      if (matchedSection && text.length > 3) {
        // Save previous section
        if (currentContent.length > 0) {
          sections[currentSection] = [...currentContent];
        }
        
        // Start new section
        currentSection = matchedSection;
        currentContent = [];
      } else if (text.length > 0) {
        // Add content to current section
        currentContent.push(text);
      }
    }

    // Save the last section
    if (currentContent.length > 0) {
      sections[currentSection] = [...currentContent];
    }

    return sections;
  }

  private extractProfileFromSections(sections: Record<string, string[]>, textItems: TextItem[]): ResumeProfile {
    const headerContent = sections['HEADER'] || [];
    const allText = Object.values(sections).flat().join(' ');
    
    // Extract name from the first few text items (usually at the top)
    const name = this.extractName(textItems);

    // Email pattern
    const emailMatch = allText.match(/[\w\.-]+@[\w\.-]+\.\w+/);
    const email = emailMatch ? emailMatch[0] : '';

    // Phone pattern  
    const phoneMatch = allText.match(/(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})/);
    const phone = phoneMatch ? phoneMatch[0] : '';

    // URL/LinkedIn pattern
    const urlMatch = allText.match(/(?:https?:\/\/)?(?:www\.)?(?:linkedin\.com\/in\/|github\.com\/|[\w\.-]+\.(?:com|org|net|io))/);
    const url = urlMatch ? urlMatch[0] : '';

    // Location - look for university/location info
    const locationMatch = allText.match(/([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,?\s*(?:University|Institute|College|Delhi|Mumbai|Bangalore|Prague|India))/);
    const location = locationMatch ? locationMatch[0] : '';

    return {
      name,
      email,
      phone,
      url,
      location,
      summary: headerContent.join(' ') // Use header content as summary
    };
  }

  private extractName(textItems: TextItem[]): string {
    // Find the largest text item or one that's likely to be a name
    if (textItems.length === 0) return '';
    
    // Sort by y position (top first) and take the first substantial text
    const sortedItems = textItems
      .filter(item => item.text.trim().length > 1)
      .sort((a, b) => b.y - a.y);
    
    // Look for name-like patterns in the first few items
    for (const item of sortedItems.slice(0, 5)) {
      const text = item.text.trim();
      // Check if it looks like a name (2-4 words, each starting with capital)
      if (/^[A-Z][a-z]+(?: [A-Z][a-z]+){1,3}$/.test(text)) {
        return text;
      }
    }
    
    // Fallback to first non-empty text
    return sortedItems[0]?.text.trim() || '';
  }

  private extractWorkExperienceFromSections(sections: Record<string, string[]>): ResumeWorkExperience[] {
    const experiences: ResumeWorkExperience[] = [];
    
    // Look for internships section (since this is a student resume)
    const internshipContent = sections['INTERNSHIPS'] || [];
    
    for (const line of internshipContent) {
      // Look for patterns like "Company Name | Position | Date"
      const internshipMatch = line.match(/([^|]+)\|([^|]+)\|(.+)/);
      if (internshipMatch) {
        experiences.push({
          company: internshipMatch[1].trim(),
          jobTitle: internshipMatch[2].trim(),
          date: internshipMatch[3].trim(),
          descriptions: []
        });
      } else if (line.includes('Research Intern') || line.includes('Intern')) {
        // Handle other internship formats
        const parts = line.split(/[,|]/).map(p => p.trim());
        if (parts.length >= 2) {
          experiences.push({
            company: parts[1] || 'Unknown Company',
            jobTitle: parts[0] || 'Intern',
            date: parts[parts.length - 1] || '',
            descriptions: parts.slice(2, -1)
          });
        }
      }
    }
    
    return experiences;
  }

  private extractEducationFromSections(sections: Record<string, string[]>): ResumeEducation[] {
    const educations: ResumeEducation[] = [];
    
    // Look for academic details and IIT course sections
    const academicContent = sections['ACADEMIC DETAILS'] || [];
    const iitCourseContent = sections['IIT COURSE'] || [];
    
    // Combine both sections for education info
    const allEducationContent = [...academicContent, ...iitCourseContent];
    
    for (const line of allEducationContent) {
      // Look for degree patterns
      if (line.includes('B.Tech') || line.includes('Bachelor') || line.includes('Master') || line.includes('PhD')) {
        const degreeMatch = line.match(/(B\.Tech|Bachelor|Master|PhD).*?(?:in\s+)?([^,\n]+)/);
        const institutionMatch = line.match(/(?:Indian Institute of Technology|IIT|University|College)([^,\n]*)/);
        const gpaMatch = line.match(/(?:CGPA|GPA)[\s:]*([0-9.]+)/);
        
        if (degreeMatch) {
          educations.push({
            degree: degreeMatch[0].trim(),
            school: institutionMatch ? institutionMatch[0].trim() : 'Unknown Institution',
            date: '',
            gpa: gpaMatch ? gpaMatch[1] : '',
            descriptions: []
          });
        }
      }
    }
    
    return educations;
  }

  private extractProjectsFromSections(sections: Record<string, string[]>): ResumeProject[] {
    const projects: ResumeProject[] = [];
    
    const projectContent = sections['PROJECTS'] || [];
    
    for (const line of projectContent) {
      // Look for project patterns with dates
      const projectMatch = line.match(/([^|]+)(?:\|.*?)?\[([^\]]+)\]/);
      if (projectMatch) {
        projects.push({
          project: projectMatch[1].trim(),
          date: projectMatch[2].trim(),
          descriptions: [line] // Store full description
        });
      } else if (line.includes('•') || line.length > 20) {
        // Handle bullet points or long descriptions
        const titleMatch = line.match(/^([^:•\n]{10,60})/);
        if (titleMatch) {
          projects.push({
            project: titleMatch[1].trim(),
            date: '',
            descriptions: [line]
          });
        }
      }
    }
    
    return projects;
  }

  private extractSkillsFromSections(sections: Record<string, string[]>): ResumeSkills {
    const skills: ResumeSkills = {
      featuredSkills: [],
      descriptions: []
    };
    
    const skillsContent = sections['TECHNICAL SKILLS'] || [];
    
    // Extract all skills from the technical skills section
    const allSkillsText = skillsContent.join(' ');
    
    // Split by common delimiters and clean up
    const skillItems = allSkillsText
      .split(/[,;•·\n]/)
      .map(s => s.trim())
      .filter(s => s.length > 2 && !s.includes('Software:'));
    
    skills.featuredSkills = skillItems.slice(0, 15).map(skill => ({
      skill: skill,
      rating: 3 // Default rating
    }));
    
    skills.descriptions = skillsContent;
    
    return skills;
  }

  async parseResume(resumeFilePath: string): Promise<void> {
    const startTime = Date.now();
    console.log(`🔍 Starting resume parsing for: ${resumeFilePath}`);

    // Validate input file
    if (!fs.existsSync(resumeFilePath)) {
      throw new Error(`Resume file not found: ${resumeFilePath}`);
    }

    if (!resumeFilePath.toLowerCase().endsWith('.pdf')) {
      throw new Error('Only PDF files are supported');
    }

    try {
      console.log('📄 Reading PDF and extracting text...');
      
      // Read PDF and extract text items
      const textItems = await this.readPdf(resumeFilePath);
      console.log(`📊 Extracted ${textItems.length} text items from PDF`);
      
      // Parse the extracted text into structured resume data
      const parsedResume = this.parseTextItems(textItems);
      
      const processingTime = Date.now() - startTime;
      console.log(`⏱️  Processing completed in ${processingTime}ms`);

      // Prepare log data with only the custom sections
      const logData = {
        timestamp: new Date().toISOString(),
        filename: path.basename(resumeFilePath),
        sections: parsedResume.custom.sections || {},
        metadata: {
          parserVersion: 'custom-parser-v1.0.0',
          processingTime,
          status: 'success'
        }
      };

      // Generate log filename and save
      const logFilename = this.generateLogFilename(resumeFilePath);
      await this.saveToLogFile(logData, logFilename);

      // Display summary
      this.displayParsingSummary(parsedResume);

    } catch (error) {
      const processingTime = Date.now() - startTime;
      console.error('❌ Error parsing resume:', error);

      // Save error log
      const errorLogData = {
        timestamp: new Date().toISOString(),
        filename: path.basename(resumeFilePath),
        sections: {},
        metadata: {
          parserVersion: 'custom-parser-v1.0.0',
          processingTime,
          status: 'error',
          errorMessage: error instanceof Error ? error.message : 'Unknown error'
        }
      };

      const logFilename = this.generateLogFilename(resumeFilePath);
      await this.saveToLogFile(errorLogData, logFilename);
      
      throw error;
    }
  }

  private displayParsingSummary(resume: Resume): void {
    console.log('\n📋 Parsing Summary:');
    console.log('==================');
    
    const { profile, workExperiences, educations, projects, skills, custom } = resume;
    
    console.log(`👤 Profile:`);
    console.log(`   Name: ${profile.name || 'Not found'}`);
    console.log(`   Email: ${profile.email || 'Not found'}`);
    console.log(`   Phone: ${profile.phone || 'Not found'}`);
    console.log(`   Location: ${profile.location || 'Not found'}`);
    console.log(`   URL: ${profile.url || 'Not found'}`);
    
    console.log(`\n💼 Work Experience/Internships: ${workExperiences.length} entries`);
    workExperiences.forEach((exp, index) => {
      console.log(`   ${index + 1}. ${exp.jobTitle} at ${exp.company} (${exp.date})`);
    });
    
    console.log(`\n🎓 Education: ${educations.length} entries`);
    educations.forEach((edu, index) => {
      console.log(`   ${index + 1}. ${edu.degree} from ${edu.school}${edu.gpa ? ` (GPA: ${edu.gpa})` : ''}`);
    });
    
    console.log(`\n🚀 Projects: ${projects.length} entries`);
    projects.forEach((proj, index) => {
      console.log(`   ${index + 1}. ${proj.project} (${proj.date})`);
    });
    
    console.log(`\n💡 Skills: ${skills.featuredSkills.length} featured skills`);
    skills.featuredSkills.slice(0, 10).forEach((skill, index) => {
      console.log(`   ${index + 1}. ${skill.skill}`);
    });

    // Display all sections found
    if (custom.sections) {
      console.log(`\n📑 Sections Extracted: ${Object.keys(custom.sections).length}`);
      Object.keys(custom.sections).forEach((sectionName, index) => {
        const itemCount = custom.sections![sectionName].length;
        console.log(`   ${index + 1}. ${sectionName} (${itemCount} items)`);
      });
    }
  }
}

// Main execution function
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('❓ Usage: node parse_resume.js <path-to-resume.pdf>');
    console.log('   Example: node parse_resume.js /path/to/resume.pdf');
    console.log('   Example: node parse_resume.js ../2023CE11156_it.pdf');
    process.exit(1);
  }

  const resumePath = args[0];
  const parser = new ResumeParser();

  try {
    await parser.parseResume(resumePath);
    console.log('\n✅ Resume parsing completed successfully!');
  } catch (error) {
    console.error('\n❌ Resume parsing failed:', error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

// Export for use as module
export { ResumeParser, ParsedResumeLog };

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}
