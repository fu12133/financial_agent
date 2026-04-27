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

    return (
      <div className="analysis-result-container">
        {/* Overall Assessment - placed at the front */}
        {analysis.overall_assessment && (
          <div style={{ 
            marginBottom: '20px', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <Text strong style={{ fontSize: '18px', color: 'white' }}>📊 Overall Assessment</Text>
              <Tag color="rgba(255,255,255,0.2)" style={{ color: 'white', border: 'none', fontSize: '14px' }}>
                {analysis.overall_assessment.recommendation}
              </Tag>
            </div>
            
            <div style={{ display: 'flex', gap: '24px', marginBottom: '16px' }}>
              <div>
                <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
                  {analysis.overall_assessment.total_score}
                </div>
                <div style={{ fontSize: '12px', opacity: 0.9 }}>Total Score</div>
              </div>
              <div>
                <div style={{ fontSize: '32px', fontWeight: 'bold' }}>
                  {(analysis.overall_assessment.confidence * 100).toFixed(0)}%
                </div>
                <div style={{ fontSize: '12px', opacity: 0.9 }}>Confidence</div>
              </div>
            </div>
            
            {analysis.overall_assessment.summary && (
              <Paragraph style={{ color: 'white', marginBottom: '12px' }}>
                {analysis.overall_assessment.summary}
              </Paragraph>
            )}
            
            {analysis.overall_assessment.key_insights && analysis.overall_assessment.key_insights.length > 0 && (
              <div>
                <Text strong style={{ color: 'white' }}>💡 Key Insights:</Text>
                <ul style={{ color: 'white', marginTop: '8px', paddingLeft: '20px' }}>
                  {analysis.overall_assessment.key_insights.slice(0, 3).map((insight: string, idx: number) => (
                    <li key={idx} style={{ marginBottom: '4px' }}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Use collapse panel to display various dimensions */}
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
          
          {/* Industry Trend */}
          {analysis.industry_trend && (
            <Panel header="📈 Industry Trend" key="industry_trend">
              <DimensionCard title="Industry Trend" icon="📈" dimension={analysis.industry_trend} />
            </Panel>
          )}
          
          {/* Competitive Landscape */}
          {analysis.competitive_landscape && (
            <Panel header="🏆 Competitive Landscape" key="competitive_landscape">
              <DimensionCard title="Competitive Landscape" icon="🏆" dimension={analysis.competitive_landscape} />
            </Panel>
          )}
          
          {/* Policy & Regulatory */}
          {analysis.policy_regulatory && (
            <Panel header="⚖️ Policy & Regulatory" key="policy_regulatory">
              <DimensionCard title="Policy & Regulatory" icon="⚖️" dimension={analysis.policy_regulatory} />
            </Panel>
          )}
          
          {/* Supply Chain Ecosystem */}
          {analysis.supply_chain_ecosystem && (
            <Panel header="🔗 Supply Chain Ecosystem" key="supply_chain_ecosystem">
              <DimensionCard title="Supply Chain Ecosystem" icon="🔗" dimension={analysis.supply_chain_ecosystem} />
            </Panel>
          )}
          
          {/* Investment Attractiveness */}
          {analysis.investment_attractiveness && (
            <Panel header="💰 Investment Attractiveness" key="investment_attractiveness">
              <DimensionCard title="Investment Attractiveness" icon="💰" dimension={analysis.investment_attractiveness} />
            </Panel>
          )}
          
          {/* Future Outlook */}
          {analysis.future_outlook && (
            <Panel header="🚀 Future Outlook" key="future_outlook">
              <DimensionCard title="Future Outlook & Impact Analysis" icon="🚀" dimension={analysis.future_outlook} isFutureOutlook={true} />
            </Panel>
          )}
        </Collapse>
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