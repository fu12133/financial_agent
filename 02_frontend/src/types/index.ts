// 故事线类型
export interface StorylineEvent {
  date: string
  event: string
  impact: string
  source_urls: string[]
}

export interface Storyline {
  summary: string
  key_events: StorylineEvent[]
  timeline: string
  key_players: string[]
  cause_effect: string
  source_urls: string[]
}

// Impact analysis dimensions
export interface ImpactDimension {
  score: number
  score_justification?: string
  analysis: string
  key_factors: string[]
  source_urls: string[]
}

// 未来展望
export interface FutureOutlook extends ImpactDimension {
  short_term_impact: string
  medium_term_impact: string
  long_term_impact: string
  risk_analysis: string
  stakeholder_impact?: {
    investors?: string
    employees?: string
    customers?: string
    partners?: string
    regulators?: string
  }
}

// Overall assessment
export interface OverallAssessment {
  total_score: number
  recommendation: string
  confidence: number
  confidence_justification?: string
  summary: string
  key_insights: string[]
  source_urls: string[]
}

// Complete analysis result
export interface AnalysisResult {
  // Storyline (common)
  storyline?: Storyline
  
  // Company analysis dimensions
  financial_impact?: ImpactDimension
  operational_impact?: ImpactDimension
  market_impact?: ImpactDimension
  regulatory_impact?: ImpactDimension
  strategic_impact?: ImpactDimension
  
  // Industry analysis dimensions
  industry_trend?: ImpactDimension
  competitive_landscape?: ImpactDimension
  policy_regulatory?: ImpactDimension
  supply_chain_ecosystem?: ImpactDimension
  investment_attractiveness?: ImpactDimension
  
  // Common dimensions
  future_outlook?: FutureOutlook
  overall_assessment?: OverallAssessment
}

// 质量评估报告
export interface QualityEvaluation {
  overall_score: number
  grade: string
  dimensions: {
    completeness: any
    traceability: any
    consistency: any
    depth: any
    timeliness: any
    balance: any
  }
  issues: string[]
  recommendations: string[]
  passed: boolean
}

// 新闻项
export interface NewsItem {
  id: string
  ticker: string
  headline: string
  summary: string
  url: string
  source: string
  publish_time: number
  sentiment_polarity: string
  sentiment_intensity: string
  event_type: string
  industry: string
}

// API 请求/响应
export interface AnalysisRequest {
  ticker?: string
  company_name?: string
  industry?: string
  industry_name?: string
  days?: number
  use_cloud?: boolean
}

export interface AnalysisResponse {
  success: boolean
  ticker?: string
  company_name?: string
  industry?: string
  industry_name?: string
  result?: {
    llm_analysis?: AnalysisResult
    quality_evaluation?: QualityEvaluation
    total_news?: number
    companies_covered?: string[]
  }
  report_path?: string
  timestamp: string
  error?: string
}