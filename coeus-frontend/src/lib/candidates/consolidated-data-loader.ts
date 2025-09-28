import { ConsolidatedCandidate, CandidateTableRow, CandidateDashboardStats } from './types';

export class ConsolidatedDataLoader {
  static async loadAllCandidates(): Promise<ConsolidatedCandidate[]> {
    try {
      // Check if running in client-side environment
      if (typeof window !== 'undefined') {
        // Client-side fallback - return mock data
        return this.getMockData();
      }

      // Server-side: dynamically import fs to avoid bundling issues
      const { promises: fs } = await import('fs');
      const path = await import('path');
      
      const CONSOLIDATED_LOGS_PATH = path.join(process.cwd(), '..', 'consolidated_logs');
      
      const files = await fs.readdir(CONSOLIDATED_LOGS_PATH);
      const jsonFiles = files.filter(file => file.endsWith('.json'));
      
      const candidates: ConsolidatedCandidate[] = [];
      
      for (const file of jsonFiles) {
        try {
          const filePath = path.join(CONSOLIDATED_LOGS_PATH, file);
          const fileContent = await fs.readFile(filePath, 'utf-8');
          const candidateData = JSON.parse(fileContent) as ConsolidatedCandidate;
          candidates.push(candidateData);
        } catch (error) {
          console.warn(`Failed to parse candidate file ${file}:`, error);
        }
      }
      
      return candidates;
    } catch (error) {
      console.warn('Failed to load consolidated logs, using mock data:', error);
      return this.getMockData();
    }
  }

  static async getCandidateTableData(): Promise<CandidateTableRow[]> {
    const candidates = await this.loadAllCandidates();
    
    return candidates.map(candidate => {
      const candidateName = this.extractCandidateName(candidate);
      const interviewDate = new Date(candidate.metadata.consolidation_timestamp).toLocaleDateString();
      
      return {
        id: candidate.candidate_scores.candidate.user_id,
        name: candidateName,
        position: this.extractPosition(candidate),
        overall_score: candidate.hirability_score?.overall_score || candidate.candidate_scores.scores.final,
        recommendation: candidate.hirability_score?.recommendation || candidate.summary.hiring_recommendation_from_lda || candidate.summary.hiring_recommendation || "Pending",
        interview_date: interviewDate,
        technical_score: candidate.hirability_score?.category_breakdown.technical_skills.score || candidate.candidate_scores.scores.components.correctness,
        communication_score: candidate.candidate_scores.scores.components.communication,
        experience_years: candidate.hirability_score?.estimated_experience_years || 0,
        status: "completed" as const
      };
    });
  }

  static async getDashboardStats(): Promise<CandidateDashboardStats> {
    const candidates = await this.loadAllCandidates();
    
    const hireCount = candidates.filter(c => {
      const recommendation = c.hirability_score?.recommendation || c.summary.hiring_recommendation_from_lda || c.summary.hiring_recommendation;
      return recommendation === "Hire";
    }).length;
    
    const totalScore = candidates.reduce((sum, c) => 
      sum + (c.hirability_score?.overall_score || c.candidate_scores.scores.final), 0
    );
    
    return {
      total_candidates: candidates.length,
      hire_recommendations: hireCount,
      average_score: candidates.length > 0 ? totalScore / candidates.length : 0,
      completed_interviews: candidates.length,
      pending_reviews: 0
    };
  }

  private static extractCandidateName(candidate: ConsolidatedCandidate): string {
    // Try to extract name from LinkedIn data first, then resume, then fallback to candidate_scores
    const linkedinData = candidate.static_knowledge.linkedin;
    const resumeData = candidate.static_knowledge.resume;
    
    // Look for name in LinkedIn data (usually first entry)
    if (linkedinData.length > 0 && linkedinData[0].trim()) {
      const firstEntry = linkedinData[0].trim();
      // If it looks like a name (not a long description)
      if (firstEntry.length < 50 && !firstEntry.includes('.') && !firstEntry.includes('@')) {
        return firstEntry;
      }
    }
    
    // Look for name in resume data (usually first entry)
    if (resumeData.length > 0 && resumeData[0].trim()) {
      const firstEntry = resumeData[0].trim();
      if (firstEntry.length < 50 && !firstEntry.includes('.') && !firstEntry.includes('@')) {
        return firstEntry;
      }
    }
    
    // Fallback to candidate_scores name
    return candidate.candidate_scores.candidate.name;
  }

  private static extractPosition(candidate: ConsolidatedCandidate): string {
    // Try to extract position from job description or LinkedIn data
    const jobDesc = candidate.job_description;
    const linkedinData = candidate.static_knowledge.linkedin;
    
    // Look for position-related keywords in job description
    if (jobDesc.length > 0) {
      const firstLine = jobDesc[0].toLowerCase();
      if (firstLine.includes('full-stack') || firstLine.includes('full stack')) {
        return 'Full Stack Developer';
      }
      if (firstLine.includes('frontend') || firstLine.includes('front-end')) {
        return 'Frontend Developer';
      }
      if (firstLine.includes('backend') || firstLine.includes('back-end')) {
        return 'Backend Developer';
      }
      if (firstLine.includes('software engineer')) {
        return 'Software Engineer';
      }
      if (firstLine.includes('data scientist')) {
        return 'Data Scientist';
      }
    }
    
    // Look for position in LinkedIn data
    for (const entry of linkedinData) {
      if (entry.includes('Software Engineer') || entry.includes('Developer') || entry.includes('Intern')) {
        if (entry.includes('Senior')) return 'Senior Software Engineer';
        if (entry.includes('Full Stack') || entry.includes('Full-Stack')) return 'Full Stack Developer';
        if (entry.includes('Frontend') || entry.includes('Front-End')) return 'Frontend Developer';
        if (entry.includes('Backend') || entry.includes('Back-End')) return 'Backend Developer';
        return 'Software Engineer';
      }
    }
    
    return 'Software Engineer'; // Default fallback
  }

  private static getMockData(): ConsolidatedCandidate[] {
    return [
      {
        metadata: {
          consolidation_timestamp: "2025-09-28T04:35:51.499167",
          consolidator_version: "1.0.0",
          sources: {
            lda_interview: true,
            code_interview: true
          }
        },
        summary: {
          overall_summary: "The candidate, Vatsal, opened the interview by claiming a senior software engineer role at Google but did not substantiate this claim. When prompted to provide a detailed, line‑by‑line architecture for server‑side rendering with React and Django, the candidate offered no technical explanation, code snippets, or design considerations, leaving the interviewer without evidence of the required depth of knowledge.",
          strengths: [
            "Demonstrated confidence by stating a senior position at a high‑profile company."
          ],
          areas_for_improvement: [
            "Did not provide any concrete technical details or code examples when asked to design a complex full‑stack solution.",
            "Failed to address key architectural components such as caching, connection pooling, and CSRF handling.",
            "Made an unverified claim about experience without supporting evidence, raising concerns about credibility."
          ],
          hiring_recommendation_from_lda: "No Hire"
        },
        static_knowledge: {
          linkedin: [
            "Vatsal Jain",
            "IIT Delhi's Electrical and Electronics Engineering program has equipped me with a solid foundation in problem-solving, teamwork, and technical excellence. During my Software Engineer Internship at Atlassian, I contributed to enhancing their data orchestration platform by enabling critical features, improving agility, and ensuring data lineage preservation, leveraging tools like Python, Airflow, and DBT.",
            "Software Engineer Intern at Atlassian · Internship (3 mos) - Bengaluru, Karnataka, India · On-site"
          ],
          resume: [
            "VATSAL JAIN",
            "B.Tech in Electrical Engineering",
            "Indian Institute of Technology Delhi",
            "GPA: 8.81",
            "Atlassian, Bangalore | Data Analytics and Platform Engineering Intern"
          ]
        },
        job_description: [
          "Design, develop, and deploy scalable and robust web applications that leverage AI and machine learning capabilities.",
          "Collaborate closely with AI/ML engineers, product managers, and UX/UI designers to translate complex AI functionalities into user-friendly features."
        ],
        lies: [],
        candidate_scores: {
          candidate: {
            name: "Vatsal Jain",
            user_id: "S2ed50e1f"
          },
          problem: {
            id: "9",
            title: "Reverse Words in a String",
            difficulty: "medium",
            language: "python"
          },
          scores: {
            final: 34,
            components: {
              correctness: 0,
              optimality: 15,
              code_quality: 0,
              understanding: 9,
              communication: 10,
              penalties: 0
            }
          },
          time_performance: {
            time_allowed_min: 20,
            time_used_min: 0,
            start_time: "2025-09-28T00:39:00.796720",
            end_time: "2025-09-27T19:13:06.014793+00:00"
          },
          test_results: {
            public_tests: [],
            hidden_tests: {
              passed: 0,
              total: 0
            }
          },
          feedback: {
            strengths: [
              "Good communication throughout",
              "Demonstrated solid understanding"
            ],
            weaknesses: [
              "Accuracy in implementation needs improvement",
              "Code organization and clarity could be enhanced"
            ],
            recommendation: "Practice fundamental algorithms and improve problem-solving approach. Consider mock interviews."
          }
        },
        hirability_score: {
          overall_score: 33.82,
          recommendation: "No Hire",
          category_breakdown: {
            technical_skills: {
              score: 29.03,
              matches: ["python", "javascript", "react", "django", "java", "c++", "sql", "mysql", "docker", "kubernetes", "git", "html", "css"],
              match_count: 13
            },
            ai_ml_experience: {
              score: 36.11,
              matches: ["machine learning", "ai", "ml", "pytorch", "tensorflow", "model", "algorithm", "pandas", "numpy", "opencv"],
              match_count: 10
            },
            experience_level: {
              score: 36.67,
              matches: ["senior", "manager", "internship", "full-time", "engineer", "software", "project", "team"],
              match_count: 8
            },
            education_background: {
              score: 33.33,
              matches: ["engineering", "bachelor", "university", "iit", "mit", "stanford", "gpa"],
              match_count: 7
            },
            soft_skills: {
              score: 37.5,
              matches: ["communication", "collaboration", "teamwork", "problem solving", "innovation", "documentation"],
              match_count: 6
            }
          },
          estimated_experience_years: 1.2,
          scoring_methodology: {
            technical_skills: "30.0%",
            ai_ml_experience: "25.0%",
            experience_level: "20.0%",
            education_background: "15.0%",
            soft_skills: "10.0%"
          },
          analysis_summary: {
            total_linkedin_claims: 60,
            total_resume_claims: 83,
            job_requirements_analyzed: 21
          }
        }
      }
    ];
  }
}
