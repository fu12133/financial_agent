import React from 'react'
import { Card, Progress, Tag, Typography, Divider } from 'antd'
import { LinkOutlined } from '@ant-design/icons'
import { ImpactDimension, FutureOutlook } from '../types'
import './DimensionCard.css'

const { Title, Paragraph, Text } = Typography

interface DimensionCardProps {
  title: string
  icon: string
  dimension: ImpactDimension | FutureOutlook
  isFutureOutlook?: boolean
}

// Remove [Source: URL] annotations from analysis text
const cleanAnalysisText = (text: string): string => {
  if (!text) return ''
  // Remove annotations in format [Source: URL]
  return text.replace(/\[参考来源[^\]]*\]/g, '').replace(/\[Source[^\]]*\]/g, '')
}

const DimensionCard: React.FC<DimensionCardProps> = ({
  title,
  icon,
  dimension,
  isFutureOutlook = false,
}) => {
  const score = dimension.score
  const scoreColor = score >= 5 ? '#52c41a' : score >= 0 ? '#faad14' : '#ff4d4f'

  const renderFutureOutlook = (fo: FutureOutlook) => (
    <div className="future-outlook">
      <div className="outlook-section">
        <Title level={5}>🚀 Short-term Impact (1-3 months)</Title>
        <Paragraph>{cleanAnalysisText(fo.short_term_impact)}</Paragraph>
      </div>

      <div className="outlook-section">
        <Title level={5}>📈 Medium-term Impact (3-12 months)</Title>
        <Paragraph>{cleanAnalysisText(fo.medium_term_impact)}</Paragraph>
      </div>

      <div className="outlook-section">
        <Title level={5}>🌟 Long-term Impact (1-3 years)</Title>
        <Paragraph>{cleanAnalysisText(fo.long_term_impact)}</Paragraph>
      </div>

      <div className="outlook-section">
        <Title level={5}>⚠️ Risk Analysis</Title>
        <Paragraph>{cleanAnalysisText(fo.risk_analysis)}</Paragraph>
      </div>

      {fo.stakeholder_impact && (
        <div className="stakeholder-section">
          <Title level={5}>👥 Stakeholder Impact</Title>
          <div className="stakeholder-grid">
            {Object.entries(fo.stakeholder_impact).map(([key, value]) => (
              <div key={key} className="stakeholder-item">
                <Text strong>{key}:</Text>
                <Paragraph>{cleanAnalysisText(value || '')}</Paragraph>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )

  return (
    <Card className="dimension-card">
      <div className="dimension-header">
        <div className="dimension-title">
          <span className="dimension-icon">{icon}</span>
          <Title level={4}>{title}</Title>
        </div>
        <div className="dimension-score">
          <Progress
            type="circle"
            percent={(score + 10) * 5}
            format={() => (
              <div className="score-display">
                <Text strong style={{ fontSize: 24, color: scoreColor }}>
                  {score > 0 ? '+' : ''}{score}
                </Text>
              </div>
            )}
            strokeColor={scoreColor}
            size={80}
          />
        </div>
      </div>

      <Divider />

      <div className="dimension-content">
        {dimension.score_justification && (
          <div className="score-justification">
            <Title level={5}>📊 Score Justification</Title>
            <Paragraph className="justification-text">{cleanAnalysisText(dimension.score_justification)}</Paragraph>
          </div>
        )}

        <Paragraph className="analysis-text">{cleanAnalysisText(dimension.analysis)}</Paragraph>

        {dimension.key_factors && dimension.key_factors.length > 0 && (
          <div className="key-factors">
            <Title level={5}>Key Factors</Title>
            <div className="factors-tags">
              {dimension.key_factors.map((factor, idx) => (
                <Tag key={idx} color="blue">{factor}</Tag>
              ))}
            </div>
          </div>
        )}

        {isFutureOutlook && renderFutureOutlook(dimension as FutureOutlook)}

        {dimension.source_urls && dimension.source_urls.length > 0 && (
          <div className="dimension-sources">
            <Title level={5}>Reference Sources</Title>
            <div className="sources-links">
              {dimension.source_urls.slice(0, 3).map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                >
                  <LinkOutlined /> Source {idx + 1}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  )
}

export default DimensionCard