import { ConsolidatedCandidate, CandidateTableRow, CandidateDashboardStats } from './types';
import { ConsolidatedDataLoader } from './consolidated-data-loader';

export class CandidateDataService {
  static async getAllCandidates(): Promise<ConsolidatedCandidate[]> {
    return ConsolidatedDataLoader.loadAllCandidates();
  }

  static async getCandidateById(id: string): Promise<ConsolidatedCandidate | null> {
    const candidates = await this.getAllCandidates();
    const candidate = candidates.find(c => c.candidate_scores.candidate.user_id === id);
    return candidate || null;
  }

  static async getCandidateTableData(): Promise<CandidateTableRow[]> {
    return ConsolidatedDataLoader.getCandidateTableData();
  }

  static async getDashboardStats(): Promise<CandidateDashboardStats> {
    return ConsolidatedDataLoader.getDashboardStats();
  }

  static extractCandidateName(candidate: ConsolidatedCandidate): string {
    // Try to extract name from LinkedIn data first, then resume, then fallback to candidate_scores
    const linkedinData = candidate.static_knowledge.linkedin;
    const resumeData = candidate.static_knowledge.resume;
    
    // Look for name in LinkedIn data (usually first entry)
    if (linkedinData.length > 0 && linkedinData[0].trim()) {
      return linkedinData[0].trim();
    }
    
    // Look for name in resume data (usually first entry)
    if (resumeData.length > 0 && resumeData[0].trim()) {
      return resumeData[0].trim();
    }
    
    // Fallback to candidate_scores name
    return candidate.candidate_scores.candidate.name;
  }

  static getRecommendationColor(recommendation: string): string {
    switch (recommendation.toLowerCase()) {
      case 'hire':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'no hire':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'maybe':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }

  static getScoreColor(score: number): string {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  }
}
