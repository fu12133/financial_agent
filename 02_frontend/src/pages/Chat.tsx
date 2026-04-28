import React, { useState } from 'react'
import { Card, Input, Button, message, List, Avatar, Typography, Tag, Collapse, Spin } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, LinkOutlined, CalendarOutlined, DownOutlined, LoadingOutlined } from '@ant-design/icons'
import { analysisAPI } from '../services/api'
import dayjs from 'dayjs'
import DimensionCard from '../components/DimensionCard'
import StorylineView from '../components/StorylineView'
import './Chat.css'

const { TextArea } = Input
const { Text, Paragraph } = Typography
const { Panel } = Collapse

interface NewsItem {
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

interface Message {
  role: 'user' | 'assistant' | 'thinking'
  content: string
  timestamp: Date
  type?: string
  data?: any
  allNews?: NewsItem[]
  displayedCount?: number
}

const NEWS_PAGE_SIZE = 10

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    // Add thinking message
    const thinkingMessageIndex = messages.length + 1
    setMessages((prev) => [
      ...prev,
      {
        role: 'thinking',
        content: 'Analyzing, please wait...',
        timestamp: new Date(),
      },
    ])

    try {
      const response = await analysisAPI.chat(inputValue)

      // Remove thinking message and add actual response
      setMessages((prev) => {
        const newMessages = prev.filter((msg) => msg.role !== 'thinking')
        const assistantMessage: Message = {
          role: 'assistant',
          content: response.response?.message || 'Sorry, I cannot answer this question',
          timestamp: new Date(),
          type: response.response?.type,
          data: response.response?.data,
        }

        // If news list, save all news and set initial display count
        if (response.response?.type === 'news_list' && response.response?.data?.news) {
          assistantMessage.allNews = response.response.data.news
          assistantMessage.displayedCount = NEWS_PAGE_SIZE
        }

        return [...newMessages, assistantMessage]
      })
    } catch (error: any) {
      console.error('Chat error:', error)
      message.error('Failed to send message')
      // Remove thinking message
      setMessages((prev) => prev.filter((msg) => msg.role !== 'thinking'))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleLoadMore = (messageIndex: number) => {
    setMessages((prev) => {
      const newMessages = [...prev]
      const msg = newMessages[messageIndex]
      if (msg && msg.allNews) {
        msg.displayedCount = Math.min(
          (msg.displayedCount || NEWS_PAGE_SIZE) + NEWS_PAGE_SIZE,
          msg.allNews.length
        )
      }
      return newMessages
    })
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'green'
      case 'negative':
        return 'red'
      default:
        return 'default'
    }
  }

  const renderNewsList = (newsData: any, messageIndex: number, allNews?: NewsItem[], displayedCount?: number) => {
    if (!allNews || allNews.length === 0) {
      return <Text>No relevant news found</Text>
    }

    const displayedNews = allNews.slice(0, displayedCount || NEWS_PAGE_SIZE)
    const hasMore = (displayedCount || NEWS_PAGE_SIZE) < allNews.length

    return (
      <div className="news-list-container">
        <List
          itemLayout="vertical"
          dataSource={displayedNews}
          renderItem={(item: NewsItem) => (
            <List.Item
              key={item.id}
              extra={
                item.url && (
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    <LinkOutlined /> Read Original
                  </a>
                )
              }
            >
              <List.Item.Meta
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong>{item.headline}</Text>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <Tag color={getSentimentColor(item.sentiment_polarity)}>
                        {item.sentiment_polarity}
                      </Tag>
                      {item.event_type && <Tag>{item.event_type}</Tag>}
                    </div>
                  </div>
                }
                description={
                  <div>
                    <CalendarOutlined />{' '}
                    {dayjs.unix(item.publish_time).format('YYYY-MM-DD HH:mm')}
                    {item.source && ` | Source: ${item.source}`}
                  </div>
                }
              />
              {item.summary && (
                <Paragraph ellipsis={{ rows: 3 }} style={{ margin: '8px 0' }}>
                  {item.summary}
                </Paragraph>
              )}
            </List.Item>
          )}
        />
        
        {hasMore && (
          <div style={{ textAlign: 'center', marginTop: '16px' }}>
            <Button
              type="default"
              icon={<DownOutlined />}
              onClick={() => handleLoadMore(messageIndex)}
            >
              Load More ({allNews.length - (displayedCount || NEWS_PAGE_SIZE)} items)
            </Button>
          </div>
        )}
        
        <div style={{ textAlign: 'center', marginTop: '8px', color: '#999', fontSize: '12px' }}>
          Showing {displayedNews.length} / {allNews.length} news items
        </div>
      </div>
    )
  }

  const renderAnalysisResult = (data: any) => {
    if (!data || !data.result || !data.result.llm_analysis) {
      return <Text>Analysis result is empty</Text>
    }

    const analysis = data.result.llm_analysis
    const qualityEval = data.result.quality_evaluation ||
        data.quality_evaluation ||
        (data.result.result && data.result.result.quality_evaluation)

    const isCompanyAnalysis = !!analysis.financial_impact

    return (
        <div className="analysis-result-container">
          {/* Overall Assessment */}
          {analysis.overall_assessment && (
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
                    Comprehensive investment analysis summary
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
                      color: analysis.overall_assessment.total_score > 0 ? '#52c41a' : analysis.overall_assessment.total_score < 0 ? '#ff4d4f' : '#faad14',
                      lineHeight: '1'
                    }}>
                      {analysis.overall_assessment.total_score > 0 ? '+' : ''}
                      {analysis.overall_assessment.total_score}
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
                    color: analysis.overall_assessment.total_score >= 10 ? '#52c41a' : analysis.overall_assessment.total_score >= 0 ? '#faad14' : '#ff4d4f',
                    padding: '8px 20px',
                    background: analysis.overall_assessment.total_score >= 10 ? '#f6ffed' : analysis.overall_assessment.total_score >= 0 ? '#fffbe6' : '#fff1f0',
                    borderRadius: '6px',
                    display: 'inline-block'
                  }}>
                    {analysis.overall_assessment.total_score >= 20 ? 'Strongly Positive Outlook' :
                        analysis.overall_assessment.total_score >= 10 ? 'Moderate Positive Outlook' :
                            analysis.overall_assessment.total_score >= 0 ? 'Slightly Positive / Neutral' :
                                analysis.overall_assessment.total_score >= -10 ? 'Moderate Negative Outlook' :
                                    'Strongly Negative Outlook'}
                  </div>
                </div>

                {/* Summary */}
                {analysis.overall_assessment.summary && (
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
                        {analysis.overall_assessment.summary}
                      </div>
                    </div>
                )}

                {/* Key Insights */}
                {analysis.overall_assessment.key_insights && analysis.overall_assessment.key_insights.length > 0 && (
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
                        {analysis.overall_assessment.key_insights.slice(0, 3).map((insight: string, idx: number) => (
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
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                      {/* Company Analysis Dimensions */}
                      {analysis.financial_impact && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Financial</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.financial_impact.score > 0 ? '#52c41a' : analysis.financial_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.financial_impact.score > 0 ? '+' : ''}{analysis.financial_impact.score}
                            </div>
                          </div>
                      )}
                      {analysis.operational_impact && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Operational</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.operational_impact.score > 0 ? '#52c41a' : analysis.operational_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.operational_impact.score > 0 ? '+' : ''}{analysis.operational_impact.score}
                            </div>
                          </div>
                      )}
                      {analysis.market_impact && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Market</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.market_impact.score > 0 ? '#52c41a' : analysis.market_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.market_impact.score > 0 ? '+' : ''}{analysis.market_impact.score}
                            </div>
                          </div>
                      )}
                      {analysis.regulatory_impact && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Regulatory</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.regulatory_impact.score > 0 ? '#52c41a' : analysis.regulatory_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.regulatory_impact.score > 0 ? '+' : ''}{analysis.regulatory_impact.score}
                            </div>
                          </div>
                      )}
                      {analysis.strategic_impact && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Strategic</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.strategic_impact.score > 0 ? '#52c41a' : analysis.strategic_impact.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.strategic_impact.score > 0 ? '+' : ''}{analysis.strategic_impact.score}
                            </div>
                          </div>
                      )}
                      
                      {/* Industry Analysis Dimensions */}
                      {analysis.industry_trend && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Industry Trend</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.industry_trend.score > 0 ? '#52c41a' : analysis.industry_trend.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.industry_trend.score > 0 ? '+' : ''}{analysis.industry_trend.score}
                            </div>
                          </div>
                      )}
                      {analysis.competitive_landscape && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Competitive</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.competitive_landscape.score > 0 ? '#52c41a' : analysis.competitive_landscape.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.competitive_landscape.score > 0 ? '+' : ''}{analysis.competitive_landscape.score}
                            </div>
                          </div>
                      )}
                      {analysis.policy_regulatory && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Policy</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.policy_regulatory.score > 0 ? '#52c41a' : analysis.policy_regulatory.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.policy_regulatory.score > 0 ? '+' : ''}{analysis.policy_regulatory.score}
                            </div>
                          </div>
                      )}
                      {analysis.supply_chain_ecosystem && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Supply Chain</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.supply_chain_ecosystem.score > 0 ? '#52c41a' : analysis.supply_chain_ecosystem.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.supply_chain_ecosystem.score > 0 ? '+' : ''}{analysis.supply_chain_ecosystem.score}
                            </div>
                          </div>
                      )}
                      {analysis.investment_attractiveness && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Investment</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.investment_attractiveness.score > 0 ? '#52c41a' : analysis.investment_attractiveness.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.investment_attractiveness.score > 0 ? '+' : ''}{analysis.investment_attractiveness.score}
                            </div>
                          </div>
                      )}
                      
                      {/* Future Outlook (Common) */}
                      {analysis.future_outlook && (
                          <div style={{
                            padding: '14px',
                            background: '#fafafa',
                            borderRadius: '8px',
                            border: '1px solid #f5f5f5',
                            textAlign: 'center'
                          }}>
                            <div style={{ fontSize: '12px', color: '#8c8c8c', marginBottom: '6px' }}>Future</div>
                            <div style={{ fontSize: '24px', fontWeight: '500', color: analysis.future_outlook.score > 0 ? '#52c41a' : analysis.future_outlook.score < 0 ? '#ff4d4f' : '#8c8c8c' }}>
                              {analysis.future_outlook.score > 0 ? '+' : ''}{analysis.future_outlook.score}
                            </div>
                          </div>
                      )}
                    </div>
                  </Panel>
                </Collapse>
              </div>
          )}

          {/* Dimension Analysis Panels */}
          <Collapse
              className="analysis-collapse"
              defaultActiveKey={['storyline']}
              accordion={false}
          >
            {/* Storyline */}
            {analysis.storyline && (
                <Panel header="📖 Storyline" key="storyline">
                  <StorylineView storyline={analysis.storyline} />
                </Panel>
            )}

            {/* Company Analysis Dimensions */}
            {isCompanyAnalysis && (
                <>
                  {analysis.financial_impact && (
                      <Panel header="💰 Financial Impact" key="financial_impact">
                        <DimensionCard title="Financial Impact" icon="💰" dimension={analysis.financial_impact} />
                      </Panel>
                  )}

                  {analysis.operational_impact && (
                      <Panel header="⚙️ Operational Impact" key="operational_impact">
                        <DimensionCard title="Operational Impact" icon="️" dimension={analysis.operational_impact} />
                      </Panel>
                  )}

                  {analysis.market_impact && (
                      <Panel header="📈 Market Impact" key="market_impact">
                        <DimensionCard title="Market Impact" icon="📈" dimension={analysis.market_impact} />
                      </Panel>
                  )}

                  {analysis.regulatory_impact && (
                      <Panel header="⚖️ Regulatory/Compliance Impact" key="regulatory_impact">
                        <DimensionCard title="Regulatory/Compliance Impact" icon="⚖️" dimension={analysis.regulatory_impact} />
                      </Panel>
                  )}

                  {analysis.strategic_impact && (
                      <Panel header="🎯 Strategic Impact" key="strategic_impact">
                        <DimensionCard title="Strategic Impact" icon="🎯" dimension={analysis.strategic_impact} />
                      </Panel>
                  )}
                </>
            )}

            {/* Industry Analysis Dimensions */}
            {!isCompanyAnalysis && (
                <>
                  {analysis.industry_trend && (
                      <Panel header="📈 Industry Trend" key="industry_trend">
                        <DimensionCard title="Industry Trend" icon="📈" dimension={analysis.industry_trend} />
                      </Panel>
                  )}

                  {analysis.competitive_landscape && (
                      <Panel header="🏆 Competitive Landscape" key="competitive_landscape">
                        <DimensionCard title="Competitive Landscape" icon="🏆" dimension={analysis.competitive_landscape} />
                      </Panel>
                  )}

                  {analysis.policy_regulatory && (
                      <Panel header="⚖️ Policy & Regulatory" key="policy_regulatory">
                        <DimensionCard title="Policy & Regulatory" icon="️" dimension={analysis.policy_regulatory} />
                      </Panel>
                  )}

                  {analysis.supply_chain_ecosystem && (
                      <Panel header="🔗 Supply Chain Ecosystem" key="supply_chain_ecosystem">
                        <DimensionCard title="Supply Chain Ecosystem" icon="" dimension={analysis.supply_chain_ecosystem} />
                      </Panel>
                  )}

                  {analysis.investment_attractiveness && (
                      <Panel header="💰 Investment Attractiveness" key="investment_attractiveness">
                        <DimensionCard title="Investment Attractiveness" icon="💰" dimension={analysis.investment_attractiveness} />
                      </Panel>
                  )}
                </>
            )}

            {/* Future Outlook */}
            {analysis.future_outlook && (
                <Panel header="🚀 Future Outlook" key="future_outlook">
                  <DimensionCard title="Future Outlook & Impact Analysis" icon="🚀" dimension={analysis.future_outlook} isFutureOutlook={true} />
                </Panel>
            )}
          </Collapse>

          {/* Quality Evaluation */}
          {qualityEval && (
              <div style={{ marginTop: '20px' }}>
                <Collapse>
                  <Panel header=" Quality Evaluation Report" key="quality">
                    <div style={{ padding: '24px' }}>
                      {/* Overall Score - Minimalist Design */}
                      <div style={{
                        marginBottom: '32px',
                        textAlign: 'center',
                        padding: '32px 24px',
                        background: '#fafafa',
                        borderRadius: '12px',
                        border: '1px solid #f0f0f0'
                      }}>
                        <div style={{
                          fontSize: '12px',
                          color: '#8c8c8c',
                          marginBottom: '16px',
                          textTransform: 'uppercase',
                          letterSpacing: '1px'
                        }}>
                          Analysis Quality
                        </div>
                        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: '8px' }}>
                          <div style={{
                            fontSize: '56px',
                            fontWeight: '300',
                            color: '#262626',
                            lineHeight: '1'
                          }}>
                            {qualityEval.overall_score?.toFixed(1) || qualityEval.overall_score}
                          </div>
                          <div style={{
                            fontSize: '20px',
                            color: '#8c8c8c',
                            fontWeight: '300'
                          }}>
                            / 100
                          </div>
                          <div style={{
                            marginLeft: '16px',
                            padding: '8px 20px',
                            background: qualityEval.grade === 'A' ? '#f6ffed' : qualityEval.grade === 'B' ? '#e6f7ff' : qualityEval.grade === 'C' ? '#fffbe6' : '#fff1f0',
                            border: `1px solid ${qualityEval.grade === 'A' ? '#b7eb8f' : qualityEval.grade === 'B' ? '#91d5ff' : qualityEval.grade === 'C' ? '#ffe58f' : '#ffccc7'}`,
                            borderRadius: '8px',
                            fontSize: '18px',
                            fontWeight: '600',
                            color: qualityEval.grade === 'A' ? '#52c41a' : qualityEval.grade === 'B' ? '#1890ff' : qualityEval.grade === 'C' ? '#faad14' : '#ff4d4f'
                          }}>
                            {qualityEval.grade}
                          </div>
                        </div>
                        <div style={{
                          fontSize: '13px',
                          color: '#8c8c8c',
                          marginTop: '16px'
                        }}>
                          {qualityEval.grade === 'A' ? 'Excellent Analysis Quality' :
                              qualityEval.grade === 'B' ? 'Good Analysis Quality' :
                                  qualityEval.grade === 'C' ? 'Fair Analysis Quality' : 'Needs Improvement'}
                        </div>
                      </div>

                      {/* Dimension Scores - Clean Grid */}
                      {qualityEval.dimensions && (
                          <div style={{ marginBottom: '32px' }}>
                            <div style={{
                              fontSize: '14px',
                              color: '#595959',
                              marginBottom: '16px',
                              fontWeight: '500'
                            }}>
                              Dimension Scores
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                              {Object.entries(qualityEval.dimensions).map(([key, value]: [string, any]) => {
                                const percentage = (value.score / value.max_score) * 100
                                const statusColor = percentage >= 80 ? '#52c41a' : percentage >= 60 ? '#1890ff' : '#ff4d4f'

                                return (
                                    <div key={key} style={{
                                      padding: '20px',
                                      background: '#ffffff',
                                      borderRadius: '10px',
                                      border: '1px solid #f0f0f0'
                                    }}>
                                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '12px' }}>
                                        <div style={{
                                          fontSize: '13px',
                                          color: '#595959',
                                          fontWeight: '500',
                                          textTransform: 'capitalize'
                                        }}>
                                          {key.replace(/_/g, ' ')}
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                                  <span style={{ fontSize: '28px', fontWeight: '500', color: statusColor }}>
                                    {value.score}
                                  </span>
                                          <span style={{ fontSize: '14px', color: '#bfbfbf' }}>
                                    / {value.max_score}
                                  </span>
                                        </div>
                                      </div>

                                      {/* Progress Bar */}
                                      <div style={{
                                        height: '4px',
                                        background: '#f5f5f5',
                                        borderRadius: '2px',
                                        overflow: 'hidden',
                                        marginBottom: '12px'
                                      }}>
                                        <div style={{
                                          width: `${percentage}%`,
                                          height: '100%',
                                          background: statusColor,
                                          borderRadius: '2px'
                                        }} />
                                      </div>

                                      {/* Reasoning/Explanation */}
                                      {value.reasoning && (
                                          <div style={{
                                            fontSize: '12px',
                                            color: '#8c8c8c',
                                            lineHeight: '1.6',
                                            padding: '10px 12px',
                                            background: '#fafafa',
                                            borderRadius: '6px'
                                          }}>
                                            <div style={{
                                              fontSize: '11px',
                                              color: '#bfbfbf',
                                              marginBottom: '4px',
                                              fontWeight: '500'
                                            }}>
                                              Score Reasoning:
                                            </div>
                                            {value.reasoning}
                                          </div>
                                      )}
                                    </div>
                                )
                              })}
                            </div>
                          </div>
                      )}

                      {/* Issues */}
                      {qualityEval.issues && qualityEval.issues.length > 0 && (
                          <div style={{
                            marginBottom: '24px',
                            padding: '16px',
                            background: '#fff2f0',
                            borderRadius: '8px',
                            border: '1px solid #ffccc7'
                          }}>
                            <div style={{
                              fontSize: '13px',
                              color: '#cf1322',
                              fontWeight: '500',
                              marginBottom: '8px'
                            }}>
                              Areas for Improvement
                            </div>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#595959' }}>
                              {qualityEval.issues.map((issue: string, idx: number) => (
                                  <li key={idx} style={{ marginBottom: '4px' }}>{issue}</li>
                              ))}
                            </ul>
                          </div>
                      )}

                      {/* Justification */}
                      {(qualityEval.justification || qualityEval.confidence_justification) && (
                          <div style={{
                            padding: '16px',
                            background: '#f9f9f9',
                            borderRadius: '8px',
                            border: '1px solid #f0f0f0'
                          }}>
                            <div style={{
                              fontSize: '13px',
                              color: '#595959',
                              fontWeight: '500',
                              marginBottom: '8px'
                            }}>
                              Evaluation Notes
                            </div>
                            <div style={{ fontSize: '13px', color: '#8c8c8c', lineHeight: '1.6' }}>
                              {qualityEval.justification || qualityEval.confidence_justification}
                            </div>
                          </div>
                      )}
                    </div>
                  </Panel>
                </Collapse>
              </div>
          )}
        </div>
    )
  }

  return (
    <div className="chat-page">
      <Card className="chat-card" title="💬 Intelligent Chat">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <RobotOutlined style={{ fontSize: 64, color: '#667eea' }} />
              <h3>Start conversation with Financial Analysis AI</h3>
              <p>I specialize in in-depth company and industry analysis. You can ask me:</p>
              <div className="suggestions">
                <Button
                  size="small"
                  onClick={() => setInputValue('Analyze Apple Inc.')}
                >
                  Analyze Apple Inc.
                </Button>
                <Button
                  size="small"
                  onClick={() => setInputValue('Analyze technology industry')}
                >
                  Analyze Technology Industry
                </Button>
                <Button
                  size="small"
                  onClick={() => setInputValue('Query latest news about AAPL')}
                >
                  Query AAPL News
                </Button>
              </div>
            </div>
          ) : (
            <List
              dataSource={messages}
              renderItem={(msg, index) => (
                <List.Item className={`message-item ${msg.role}`}>
                  <Avatar
                    icon={
                      msg.role === 'user' ? (
                        <UserOutlined />
                      ) : msg.role === 'thinking' ? (
                        <LoadingOutlined spin />
                      ) : (
                        <RobotOutlined />
                      )
                    }
                    style={{
                      backgroundColor:
                        msg.role === 'user'
                          ? '#667eea'
                          : msg.role === 'thinking'
                          ? '#faad14'
                          : '#764ba2',
                    }}
                  />
                  <div className="message-content">
                    {msg.role === 'thinking' ? (
                      <div className="thinking-message">
                        <Spin indicator={<LoadingOutlined spin />} size="small" />
                        <span style={{ marginLeft: '8px' }}>{msg.content}</span>
                      </div>
                    ) : (
                      <>
                        <div className="message-text">{msg.content}</div>

                        {/* If news list type, render news */}
                        {msg.type === 'news_list' && (
                          <div style={{ marginTop: '12px' }}>
                            {renderNewsList(msg.data, index, msg.allNews, msg.displayedCount)}
                          </div>
                        )}

                        {/* If analysis result type, render analysis content */}
                        {msg.type === 'analysis_result' && msg.data && (
                          <div style={{ marginTop: '12px' }}>
                            {renderAnalysisResult(msg.data)}
                          </div>
                        )}

                        <div className="message-time">
                          {msg.timestamp.toLocaleTimeString()}
                        </div>
                      </>
                    )}
                  </div>
                </List.Item>
              )}
            />
          )}
        </div>

        <div className="input-area">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your question..."
            autoSize={{ minRows: 2, maxRows: 6 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            disabled={!inputValue.trim()}
          >
            Send
          </Button>
        </div>
      </Card>
    </div>
  )
}

export default Chat