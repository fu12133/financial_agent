import React, { useState } from 'react'
import {
  Card,
  Form,
  Button,
  Select,
  message,
  Spin,
  Tabs,
  Row,
  Col,
  Collapse,
} from 'antd'
import { SearchOutlined, ReloadOutlined, DownOutlined } from '@ant-design/icons'
import { analysisAPI } from '../services/api'
import { AnalysisResult, QualityEvaluation } from '../types'
import StorylineView from '../components/StorylineView'
import DimensionCard from '../components/DimensionCard'
import QualityReport from '../components/QualityReport'
import './CompanyAnalysis.css'

const { Option } = Select
const { Panel } = Collapse

const CompanyAnalysis: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [qualityEval, setQualityEval] = useState<QualityEvaluation | null>(null)

  const popularTickers = [
    { value: 'AAPL', label: 'Apple Inc.' },
    { value: 'MSFT', label: 'Microsoft' },
    { value: 'GOOGL', label: 'Google' },
    { value: 'AMZN', label: 'Amazon' },
    { value: 'TSLA', label: 'Tesla' },
    { value: 'META', label: 'Meta' },
    { value: 'NVDA', label: 'NVIDIA' },
  ]

  const handleSubmit = async (values: any) => {
    setLoading(true)
    try {
      console.log('🚀 Starting company analysis request...')
      console.log('Request parameters:', values)

      const response = await analysisAPI.analyzeCompany({
        ticker: values.ticker,
        days: 7,
        use_cloud: true,
      })

      console.log('✅ Response received')
      console.log('📊 Full response object:', response)
      console.log('📊 response.success:', response.success)
      console.log('📊 response.result:', response.result)
      console.log('📊 response.error:', response.error)

      if (response.result) {
        console.log('📊 result type:', typeof response.result)
        console.log('📊 result keys:', Object.keys(response.result))
        console.log('📊 result.llm_analysis exists:', !!response.result.llm_analysis)
        console.log('📊 result.quality_evaluation exists:', !!response.result.quality_evaluation)
        
        if (response.result.llm_analysis) {
          console.log('📊 llm_analysis keys:', Object.keys(response.result.llm_analysis))
          console.log('📊 Has financial_impact:', !!response.result.llm_analysis.financial_impact)
          console.log('📊 Has operational_impact:', !!response.result.llm_analysis.operational_impact)
          console.log('📊 Has market_impact:', !!response.result.llm_analysis.market_impact)
          console.log('📊 Has regulatory_impact:', !!response.result.llm_analysis.regulatory_impact)
          console.log('📊 Has strategic_impact:', !!response.result.llm_analysis.strategic_impact)
          console.log('📊 Has future_outlook:', !!response.result.llm_analysis.future_outlook)
        } else {
          console.error('❌ llm_analysis is missing!')
          console.error('   Full result structure:', JSON.stringify(response.result, null, 2))
        }
      }

      if (response.success && response.result?.llm_analysis) {
        console.log('✅ Setting analysis result and quality evaluation')
        setResult(response.result.llm_analysis)
        setQualityEval(response.result.quality_evaluation || null)
        console.log('📊 Quality eval set to:', response.result.quality_evaluation ? 'present' : 'null')
        message.success('✅ Company analysis completed!')
      } else {
        console.error('❌ Analysis failure reason:')
        console.error('   success:', response.success)
        console.error('   has result:', !!response.result)
        console.error('   has llm_analysis:', !!response.result?.llm_analysis)
        console.error('   error:', response.error)
        if (!response.result?.llm_analysis) {
          console.error('   ⚠️ Missing llm_analysis in response!')
          console.error('   Response structure:', JSON.stringify(response, null, 2))
        }
        message.error(response.error || 'Analysis failed, please check backend logs')
      }
    } catch (error: any) {
      console.error('❌ Request error:', error)
      console.error('❌ Error details:', error.response?.data)
      message.error('Request failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    form.resetFields()
    setResult(null)
    setQualityEval(null)
  }

  return (
    <div className="company-analysis-page">
      <Card className="search-card" title="🏢 Company Analysis Search">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ days: 7 }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="ticker"
                label="Stock Ticker"
                rules={[{ required: true, message: 'Please enter stock ticker' }]}
              >
                <Select
                  showSearch
                  placeholder="Enter or select stock ticker"
                  size="large"
                  optionFilterProp="children"
                >
                  {popularTickers.map((ticker) => (
                    <Option key={ticker.value} value={ticker.value}>
                      {ticker.value} - {ticker.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="Analysis Period">
                <div style={{ padding: '8px 11px', background: '#f5f5f5', borderRadius: 4 }}>
                  Last 7 days
                </div>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={24}>
              <Form.Item>
                <div style={{ display: 'flex', gap: 12 }}>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<SearchOutlined />}
                    size="large"
                    loading={loading}
                    block
                  >
                    Start Analysis
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    size="large"
                    onClick={handleReset}
                    disabled={loading}
                  >
                    Reset
                  </Button>
                </div>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {loading && (
        <div className="loading-container">
          <Spin size="large" tip="AI analysis in progress, please wait..." />
          <p>Analysis may take 1-3 minutes, please be patient</p>
        </div>
      )}

      {!loading && result && (
        <div className="results-container">
          {/* Overall Assessment */}
          {result.overall_assessment && (
            <div style={{
              marginBottom: '20px',
              padding: '32px',
              background: '#ffffff',
              borderRadius: '12px',
              border: '1px solid #f0f0f0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
            }}>
              {/* Header */}
              <div style={{ marginBottom: '24px' }}>
                <div style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#262626',
                  marginBottom: '4px'
                }}>
                  Overall Assessment
                </div>
                <div style={{
                  fontSize: '13px',
                  color: '#8c8c8c'
                }}>
                  Comprehensive company analysis summary
                </div>
              </div>

              {/* Total Score */}
              <div style={{
                marginBottom: '28px',
                padding: '28px',
                background: '#fafafa',
                borderRadius: '10px',
                textAlign: 'center',
                border: '1px solid #f5f5f5'
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: '10px', marginBottom: '12px' }}>
                  <div style={{
                    fontSize: '52px',
                    fontWeight: '300',
                    color: result.overall_assessment.total_score > 0 ? '#52c41a' : result.overall_assessment.total_score < 0 ? '#ff4d4f' : '#faad14',
                    lineHeight: '1'
                  }}>
                    {result.overall_assessment.total_score > 0 ? '+' : ''}
                    {result.overall_assessment.total_score}
                  </div>
                  <div style={{
                    fontSize: '18px',
                    color: '#bfbfbf',
                    fontWeight: '300'
                  }}>
                    / 60
                  </div>
                </div>

                <div style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: result.overall_assessment.total_score >= 10 ? '#52c41a' : result.overall_assessment.total_score >= 0 ? '#faad14' : '#ff4d4f',
                  padding: '8px 20px',
                  background: result.overall_assessment.total_score >= 10 ? '#f6ffed' : result.overall_assessment.total_score >= 0 ? '#fffbe6' : '#fff1f0',
                  borderRadius: '6px',
                  display: 'inline-block'
                }}>
                  {result.overall_assessment.total_score >= 20 ? 'Strongly Positive Outlook' :
                      result.overall_assessment.total_score >= 10 ? 'Moderate Positive Outlook' :
                          result.overall_assessment.total_score >= 0 ? 'Slightly Positive / Neutral' :
                              result.overall_assessment.total_score >= -10 ? 'Moderate Negative Outlook' :
                                  'Strongly Negative Outlook'}
                </div>
              </div>

              {/* Summary */}
              {result.overall_assessment.summary && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#262626',
                    marginBottom: '10px'
                  }}>
                    Analysis Summary
                  </div>
                  <div style={{
                    fontSize: '14px',
                    color: '#595959',
                    lineHeight: '1.7'
                  }}>
                    {result.overall_assessment.summary}
                  </div>
                </div>
              )}

              {/* Key Insights */}
              {result.overall_assessment.key_insights && result.overall_assessment.key_insights.length > 0 && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#262626',
                    marginBottom: '12px'
                  }}>
                    Key Insights
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {result.overall_assessment.key_insights.slice(0, 3).map((insight: string, idx: number) => (
                      <div key={idx} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px',
                        padding: '12px 16px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        fontSize: '13px',
                        color: '#595959',
                        lineHeight: '1.6',
                        border: '1px solid #f5f5f5'
                      }}>
                        <span style={{ color: '#faad14', fontSize: '16px', lineHeight: '1', marginTop: '1px' }}>•</span>
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detailed Dimension Scores (Collapsible) */}
              <Collapse
                ghost
                style={{ background: 'transparent', border: 'none' }}
                expandIconPosition="right"
              >
                <Panel
                  header={
                    <div style={{ fontSize: '13px', color: '#595959', fontWeight: '500' }}>
                      View Detailed Dimension Scores
                    </div>
                  }
                  key="details"
                >
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
                    {/* Company Analysis Dimensions */}
                    {result.financial_impact && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Financial</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.financial_impact.score > 0 ? '#52c41a' : result.financial_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.financial_impact.score > 0 ? '+' : ''}{result.financial_impact.score}
                        </div>
                      </div>
                    )}
                    {result.operational_impact && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Operational</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.operational_impact.score > 0 ? '#52c41a' : result.operational_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.operational_impact.score > 0 ? '+' : ''}{result.operational_impact.score}
                        </div>
                      </div>
                    )}
                    {result.market_impact && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Market</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.market_impact.score > 0 ? '#52c41a' : result.market_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.market_impact.score > 0 ? '+' : ''}{result.market_impact.score}
                        </div>
                      </div>
                    )}
                    {result.regulatory_impact && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Regulatory</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.regulatory_impact.score > 0 ? '#52c41a' : result.regulatory_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.regulatory_impact.score > 0 ? '+' : ''}{result.regulatory_impact.score}
                        </div>
                      </div>
                    )}
                    {result.strategic_impact && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Strategic</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.strategic_impact.score > 0 ? '#52c41a' : result.strategic_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.strategic_impact.score > 0 ? '+' : ''}{result.strategic_impact.score}
                        </div>
                      </div>
                    )}
                    {result.future_outlook && (
                      <div style={{
                        padding: '14px',
                        background: '#fafafa',
                        borderRadius: '8px',
                        border: '1px solid #f5f5f5',
                        textAlign: 'center'
                      }}>
                        <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Future</div>
                        <div style={{ fontSize: '24px', fontWeight: '500', color: result.future_outlook.score > 0 ? '#52c41a' : result.future_outlook.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                          {result.future_outlook.score > 0 ? '+' : ''}{result.future_outlook.score}
                        </div>
                      </div>
                    )}
                  </div>
                </Panel>
              </Collapse>
            </div>
          )}

          {result.storyline && <StorylineView storyline={result.storyline} />}

          <Tabs
            defaultActiveKey="dimensions"
            items={[
              {
                key: 'dimensions',
                label: '📊 Five-Dimensional Impact Analysis',
                children: (
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      {result.financial_impact && (
                        <DimensionCard
                          title="Financial Impact"
                          icon="💰"
                          dimension={result.financial_impact}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.operational_impact && (
                        <DimensionCard
                          title="Operational Impact"
                          icon="⚙️"
                          dimension={result.operational_impact}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.market_impact && (
                        <DimensionCard
                          title="Market Impact"
                          icon="📈"
                          dimension={result.market_impact}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.regulatory_impact && (
                        <DimensionCard
                          title="Regulatory/Compliance Impact"
                          icon="⚖️"
                          dimension={result.regulatory_impact}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.strategic_impact && (
                        <DimensionCard
                          title="Strategic Impact"
                          icon="🎯"
                          dimension={result.strategic_impact}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.future_outlook && (
                        <DimensionCard
                          title="Future Outlook & Impact Analysis"
                          icon="🚀"
                          dimension={result.future_outlook}
                          isFutureOutlook={true}
                        />
                      )}
                    </Col>
                  </Row>
                ),
              },
              qualityEval && {
                key: 'quality',
                label: '✅ Quality Evaluation',
                children: <QualityReport evaluation={qualityEval} />,
              },
            ].filter(Boolean)}
          />
        </div>
      )}
    </div>
  )
}

export default CompanyAnalysis