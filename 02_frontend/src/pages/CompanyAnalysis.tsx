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
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { analysisAPI } from '../services/api'
import { AnalysisResult, QualityEvaluation } from '../types'
import StorylineView from '../components/StorylineView'
import DimensionCard from '../components/DimensionCard'
import QualityReport from '../components/QualityReport'
import './CompanyAnalysis.css'

const { Option } = Select

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
        console.log('📊 result.llm_analysis:', response.result.llm_analysis)

        if (response.result.llm_analysis) {
          console.log('📊 llm_analysis type:', typeof response.result.llm_analysis)
          console.log('📊 llm_analysis keys:', Object.keys(response.result.llm_analysis))
          console.log('📊 storyline:', response.result.llm_analysis.storyline)
          console.log('📊 financial_impact:', response.result.llm_analysis.financial_impact)
        }
      }

      if (response.success && response.result?.llm_analysis) {
        setResult(response.result.llm_analysis)
        setQualityEval(response.result.quality_evaluation || null)
        message.success('✅ Company analysis completed!')
      } else {
        console.error('❌ Analysis failure reason:')
        console.error('   success:', response.success)
        console.error('   result:', response.result)
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