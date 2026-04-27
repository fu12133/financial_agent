import React, { useState } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  DatePicker,
  message,
  Spin,
  Tabs,
  Row,
  Col,
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { analysisAPI } from '../services/api'
import { AnalysisResult, QualityEvaluation } from '../types'
import StorylineView from '../components/StorylineView'
import DimensionCard from '../components/DimensionCard'
import QualityReport from '../components/QualityReport'
import dayjs from 'dayjs'
import './IndustryAnalysis.css'

const { Option } = Select
const { TextArea } = Input

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
      const response = await analysisAPI.analyzeIndustry({
        industry: values.industry,
        days: 7,  // Fixed 7 days
        use_cloud: true,
      })

      console.log('✅ Response received')
      console.log('📊 Full response object:', response)
      console.log('📊 response.success:', response.success)
      console.log('📊 response.result:', response.result)
      
      if (response.result) {
        console.log('📊 result keys:', Object.keys(response.result))
        console.log('📊 result.llm_analysis:', response.result.llm_analysis)
        
        if (response.result.llm_analysis) {
          console.log('📊 llm_analysis keys:', Object.keys(response.result.llm_analysis))
        }
      }

      if (response.success && response.result?.llm_analysis) {
        setResult(response.result.llm_analysis)
        setQualityEval(response.result.quality_evaluation || null)
        message.success('✅ Industry analysis completed!')
      } else {
        console.error('❌ Analysis failure reason:')
        console.error('   success:', response.success)
        console.error('   error:', response.error)
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
    <div className="industry-analysis-page">
      <Card className="search-card" title="🔍 Industry Analysis Search">
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
                <Select placeholder="Please select an industry to analyze" size="large">
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
          {result.storyline && <StorylineView storyline={result.storyline} />}

          <Tabs
            defaultActiveKey="dimensions"
            items={[
              {
                key: 'dimensions',
                label: '📊 Industry Impact Analysis',
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
                          icon="🏆"
                          dimension={result.competitive_landscape}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.policy_regulatory && (
                        <DimensionCard
                          title="Policy & Regulatory"
                          icon="⚖️"
                          dimension={result.policy_regulatory}
                        />
                      )}
                    </Col>
                    <Col span={24}>
                      {result.supply_chain_ecosystem && (
                        <DimensionCard
                          title="Supply Chain Ecosystem"
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