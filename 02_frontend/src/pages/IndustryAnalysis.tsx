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
import './IndustryAnalysis.css'

const { Option } = Select
const { Panel } = Collapse

const IndustryAnalysis: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [qualityEval, setQualityEval] = useState<QualityEvaluation | null>(null)

  const industryOptions = [
    { value: 'technology', label: 'Technology Industry' },
    { value: 'finance', label: 'Finance Industry' },
    { value: 'healthcare_pharma', label: 'Healthcare & Pharmaceuticals' },
    { value: 'consumer_retail', label: 'Consumer Retail' },
    { value: 'energy_utilities', label: 'Energy & Utilities' },
    { value: 'automotive_manufacturing', label: 'Automotive & Manufacturing' },
    { value: 'real_estate', label: 'Real Estate' },
    { value: 'telecommunications', label: 'Telecommunications' },
  ]

  const handleSubmit = async (values: any) => {
    setLoading(true)
    try {
      console.log('🚀 Starting industry analysis request...')
      console.log('Request parameters:', values)

      const response = await analysisAPI.analyzeIndustry({
        industry: values.industry,
        days: 7,
        use_cloud: true,
      })

      console.log('✅ Response received')
      console.log(' Full response object:', response)
      console.log('📊 response.success:', response.success)
      console.log('📊 response.result:', response.result)
      console.log('📊 response.error:', response.error)

      if (response.result) {
        console.log('📊 result type:', typeof response.result)
        console.log('📊 result keys:', Object.keys(response.result))
        console.log(' result.llm_analysis exists:', !!response.result.llm_analysis)
        console.log('📊 result.quality_evaluation exists:', !!response.result.quality_evaluation)
        
        if (response.result.llm_analysis) {
          console.log('📊 llm_analysis keys:', Object.keys(response.result.llm_analysis))
          console.log('📊 Has industry_trend:', !!response.result.llm_analysis.industry_trend)
          console.log('📊 Has competitive_landscape:', !!response.result.llm_analysis.competitive_landscape)
          console.log('📊 Has policy_regulatory:', !!response.result.llm_analysis.policy_regulatory)
          console.log('📊 Has supply_chain_ecosystem:', !!response.result.llm_analysis.supply_chain_ecosystem)
          console.log('📊 Has investment_attractiveness:', !!response.result.llm_analysis.investment_attractiveness)
          console.log('📊 Has future_outlook:', !!response.result.llm_analysis.future_outlook)
        } else {
          console.error(' llm_analysis is missing!')
          console.error('   Full result structure:', JSON.stringify(response.result, null, 2))
        }
      }

      if (response.success && response.result?.llm_analysis) {
        console.log('✅ Setting analysis result and quality evaluation')
        setResult(response.result.llm_analysis)
        setQualityEval(response.result.quality_evaluation || null)
        console.log('📊 Quality eval set to:', response.result.quality_evaluation ? 'present' : 'null')
        message.success('✅ Industry analysis completed!')
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
      console.error(' Request error:', error)
      console.error(' Error details:', error.response?.data)
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
    <div className="industry-analysis-page">
      <Card className="search-card" title="🏭 Industry Analysis Search">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{ days: 7 }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="industry"
                label="Select Industry"
                rules={[{ required: true, message: 'Please select an industry' }]}
              >
                <Select
                  showSearch
                  placeholder="Select industry to analyze"
                  size="large"
                  optionFilterProp="children"
                >
                  {industryOptions.map((option) => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
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
                    Comprehensive industry analysis summary
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
                      {/* Industry Analysis Dimensions */}
                      {result.industry_trend && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Industry Trend</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: result.industry_trend.score > 0 ? '#52c41a' : result.industry_trend.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {result.industry_trend.score > 0 ? '+' : ''}{result.industry_trend.score}
                            </div>
                          </div>
                      )}
                      {result.competitive_landscape && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Competitive</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: result.competitive_landscape.score > 0 ? '#52c41a' : result.competitive_landscape.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {result.competitive_landscape.score > 0 ? '+' : ''}{result.competitive_landscape.score}
                            </div>
                          </div>
                      )}
                      {result.policy_regulatory && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Policy</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: result.policy_regulatory.score > 0 ? '#52c41a' : result.policy_regulatory.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {result.policy_regulatory.score > 0 ? '+' : ''}{result.policy_regulatory.score}
                            </div>
                          </div>
                      )}
                      {result.supply_chain_ecosystem && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Supply Chain</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: result.supply_chain_ecosystem.score > 0 ? '#52c41a' : result.supply_chain_ecosystem.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {result.supply_chain_ecosystem.score > 0 ? '+' : ''}{result.supply_chain_ecosystem.score}
                            </div>
                          </div>
                      )}
                      {result.investment_attractiveness && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Investment</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: result.investment_attractiveness.score > 0 ? '#52c41a' : result.investment_attractiveness.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {result.investment_attractiveness.score > 0 ? '+' : ''}{result.investment_attractiveness.score}
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
                label: '📊 Five-Dimensional Industry Analysis',
                children: (
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      {result.industry_trend && (
                        <DimensionCard
                          title="Industry Trend"
                          icon="📈"
                          dimension={result.industry_trend}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.competitive_landscape && (
                        <DimensionCard
                          title="Competitive Landscape"
                          icon=""
                          dimension={result.competitive_landscape}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.policy_regulatory && (
                        <DimensionCard
                          title="Policy & Regulatory Environment"
                          icon="⚖️"
                          dimension={result.policy_regulatory}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.supply_chain_ecosystem && (
                        <DimensionCard
                          title="Supply Chain & Ecosystem"
                          icon="🔗"
                          dimension={result.supply_chain_ecosystem}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.investment_attractiveness && (
                        <DimensionCard
                          title="Investment Attractiveness"
                          icon="💰"
                          dimension={result.investment_attractiveness}
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

export default IndustryAnalysis