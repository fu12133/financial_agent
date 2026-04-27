import React from 'react'
import { Card, Timeline, Tag, Typography, Divider } from 'antd'
import { ClockCircleOutlined, LinkOutlined } from '@ant-design/icons'
import { Storyline } from '../types'
import './StorylineView.css'

const { Title, Paragraph, Text } = Typography

interface StorylineViewProps {
  storyline: Storyline
}

// Remove [Source: URL] annotations from text
const cleanText = (text: string): string => {
  if (!text) return ''
  return text.replace(/\[参考来源[^\]]*\]/g, '').replace(/\[Source[^\]]*\]/g, '')
}

const StorylineView: React.FC<StorylineViewProps> = ({ storyline }) => {
  return (
    <Card className="storyline-card" title="📖 Event Timeline & Storyline">
      <div className="storyline-summary">
        <Paragraph strong>{cleanText(storyline.summary)}</Paragraph>
      </div>

      <Divider />

      <div className="timeline-section">
        <Title level={5}>Key Timeline</Title>
        <Timeline
          items={storyline.key_events.map((event, index) => ({
            color: 'blue',
            dot: <ClockCircleOutlined style={{ fontSize: '16px' }} />,
            children: (
              <div className="timeline-item">
                <div className="timeline-date">{event.date}</div>
                <div className="timeline-event">
                  <Text strong>{cleanText(event.event)}</Text>
                </div>
                <div className="timeline-impact">
                  <Tag color="purple">Impact</Tag>
                  {cleanText(event.impact)}
                </div>
                {event.source_urls && event.source_urls.length > 0 && (
                  <div className="timeline-sources">
                    {event.source_urls.slice(0, 2).map((url, idx) => (
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
                )}
              </div>
            ),
          }))}
        />
      </div>

      <Divider />

      <div className="storyline-details">
        <div className="detail-item">
          <Title level={5}>Key Participants</Title>
          <div className="players-tags">
            {storyline.key_players.map((player, idx) => (
              <Tag key={idx} color="blue">{player}</Tag>
            ))}
          </div>
        </div>

        <div className="detail-item">
          <Title level={5}>Cause and Effect</Title>
          <Paragraph>{cleanText(storyline.cause_effect)}</Paragraph>
        </div>

        <div className="detail-item">
          <Title level={5}>Development Timeline</Title>
          <Paragraph>{cleanText(storyline.timeline)}</Paragraph>
        </div>
      </div>

      {storyline.source_urls && storyline.source_urls.length > 0 && (
        <>
          <Divider />
          <div className="storyline-sources">
            <Title level={5}>Reference Sources</Title>
            <div className="sources-list">
              {storyline.source_urls.slice(0, 5).map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                >
                  <LinkOutlined /> {url.substring(0, 60)}...
                </a>
              ))}
            </div>
          </div>
        </>
      )}
    </Card>
  )
}

export default StorylineView