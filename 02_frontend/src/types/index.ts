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

// 影响分析维度
export interface ImpactDimension {
  score: number
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

// 总体评估
export interface OverallAssessment {
  total_score: number
  recommendation: string
  confidence: number
  summary: string
  key_insights: string[]
  source_urls: string[]
}

// 完整分析结果
export interface AnalysisResult {
  storyline?: Storyline
  financial_impact?: ImpactDimension
  operational_impact?: ImpactDimension
  market_impact?: ImpactDimension
  regulatory_impact?: ImpactDimension
  strategic_impact?: ImpactDimension
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