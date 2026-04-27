import React from 'react'
import { Card, Row, Col, Typography, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import {
  BarChartOutlined,
  PieChartOutlined,
  MessageOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons'
import './Home.css'

const { Title, Paragraph } = Typography

const Home: React.FC = () => {
  const navigate = useNavigate()

  const features = [
    {
      title: 'Company Analysis',
      icon: <BarChartOutlined style={{ fontSize: 48, color: '#667eea' }} />,
      description: 'Five-dimensional impact analysis based on latest news, including event timeline and future outlook',
      path: '/company',
      color: '#667eea',
    },
    {
      title: 'Industry Analysis',
      icon: <PieChartOutlined style={{ fontSize: 48, color: '#764ba2' }} />,
      description: 'Comprehensive industry trend analysis, competitive landscape and investment attractiveness assessment',
      path: '/industry',
      color: '#764ba2',
    },
    {
      title: 'Intelligent Chat',
      icon: <MessageOutlined style={{ fontSize: 48, color: '#f093fb' }} />,
      description: 'Natural conversation with AI Agent to get personalized financial analysis recommendations',
      path: '/chat',
      color: '#f093fb',
    },
  ]

  return (
    <div className="home-page">
      <div className="hero-section">
        <Title level={1} className="hero-title">
          🚀 Financial Analysis AI Agent
        </Title>
        <Paragraph className="hero-subtitle">
          Intelligent financial analysis system based on RAG + LLM, providing traceable and high-quality company and industry analysis
        </Paragraph>
      </div>

      <Row gutter={[24, 24]} className="features-grid">
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={8} key={index}>
            <Card
              hoverable
              className="feature-card"
              onClick={() => navigate(feature.path)}
            >
              <div className="feature-icon">{feature.icon}</div>
              <Title level={3}>{feature.title}</Title>
              <Paragraph>{feature.description}</Paragraph>
              <Button
                type="primary"
                size="large"
                icon={<ArrowRightOutlined />}
                style={{ backgroundColor: feature.color, borderColor: feature.color }}
              >
                Get Started
              </Button>
            </Card>
          </Col>
        ))}
      </Row>

      <div className="tech-stack">
        <Title level={4}>Technology Stack</Title>
        <div className="tech-tags">
          <span className="tech-tag">React + TypeScript</span>
          <span className="tech-tag">FastAPI</span>
          <span className="tech-tag">RAG Retrieval</span>
          <span className="tech-tag">Qwen LLM</span>
          <span className="tech-tag">Milvus Vector Database</span>
          <span className="tech-tag">BGE-M3 Embedding</span>
        </div>
      </div>
    </div>
  )
}

export default Home