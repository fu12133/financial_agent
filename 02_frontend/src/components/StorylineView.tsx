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
          Event Timeline & Storyline
        </div>
        <div style={{
          fontSize: '13px',
          color: '#8c8c8c'
        }}>
          Key events and development timeline
        </div>
      </div>

      {/* Summary */}
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
          {cleanText(storyline.summary)}
        </div>
      </div>

      <Divider style={{ margin: '24px 0' }} />

      {/* Key Timeline */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: '600',
          color: '#262626',
          marginBottom: '16px'
        }}>
          Key Timeline
        </div>
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
                <div className="timeline-impact" style={{ marginTop: '8px' }}>
                  <Tag color="purple">Impact</Tag>
                  {cleanText(event.impact)}
                </div>
                {event.source_urls && event.source_urls.length > 0 && (
                  <div className="timeline-sources" style={{ marginTop: '8px' }}>
                    {event.source_urls.slice(0, 2).map((url, idx) => (
                      <a
                        key={idx}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                        style={{ marginRight: '12px', fontSize: '12px', color: '#1890ff' }}
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

      <Divider style={{ margin: '24px 0' }} />

      {/* Details Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Key Participants */}
        <div>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#262626',
            marginBottom: '12px'
          }}>
            Key Participants
          </div>
          <div className="players-tags" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {storyline.key_players.map((player, idx) => (
              <Tag key={idx} color="blue" style={{ fontSize: '13px', padding: '4px 12px' }}>{player}</Tag>
            ))}
          </div>
        </div>

        {/* Cause and Effect */}
        <div>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#262626',
            marginBottom: '10px'
          }}>
            Cause and Effect
          </div>
          <div style={{
            fontSize: '14px',
            color: '#595959',
            lineHeight: '1.7'
          }}>
            {cleanText(storyline.cause_effect)}
          </div>
        </div>

        {/* Development Timeline */}
        <div>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#262626',
            marginBottom: '10px'
          }}>
            Development Timeline
          </div>
          <div style={{
            fontSize: '14px',
            color: '#595959',
            lineHeight: '1.7'
          }}>
            {cleanText(storyline.timeline)}
          </div>
        </div>
      </div>

      {/* Reference Sources */}
      {storyline.source_urls && storyline.source_urls.length > 0 && (
        <>
          <Divider style={{ margin: '24px 0' }} />
          <div>
            <div style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#262626',
              marginBottom: '12px'
            }}>
              Reference Sources
            </div>
            <div className="sources-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {storyline.source_urls.slice(0, 5).map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                  style={{ fontSize: '13px', color: '#1890ff' }}
                >
                  <LinkOutlined /> {url.substring(0, 80)}{url.length > 80 ? '...' : ''}
                </a>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default StorylineView