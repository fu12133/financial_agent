import React from 'react'
import { Card, Progress, Alert, List, Tag, Divider, Typography } from 'antd'
import { CheckCircleOutlined, WarningOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { QualityEvaluation } from '../types'
import './QualityReport.css'

const { Title, Paragraph, Text } = Typography

interface QualityReportProps {
  evaluation: QualityEvaluation
}

const QualityReport: React.FC<QualityReportProps> = ({ evaluation }) => {
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return '#52c41a'
      case 'B': return '#1890ff'
      case 'C': return '#faad14'
      case 'D': return '#ff7a45'
      case 'F': return '#ff4d4f'
      default: return '#d9d9d9'
    }
  }

  const dimensionNames: Record<string, string> = {
    completeness: 'Completeness',
    traceability: 'Traceability',
    consistency: 'Consistency',
    depth: 'Depth',
    timeliness: 'Timeliness',
    balance: 'Balance',
  }

  return (
    <Card className="quality-report-card">
      <Title level={4}>Quality Evaluation Report</Title>
      <Paragraph type="secondary">Analysis quality assessment summary</Paragraph>

      <div className="overall-score">
        <div className="score-circle">
          <Progress
            type="dashboard"
            percent={evaluation.overall_score}
            format={() => (
              <div className="grade-display">
                <div
                  className="grade-letter"
                  style={{ color: getGradeColor(evaluation.grade) }}
                >
                  {evaluation.grade}
                </div>
                <div className="grade-score">{evaluation.overall_score.toFixed(1)}</div>
              </div>
            )}
            strokeColor={getGradeColor(evaluation.grade)}
          />
        </div>
        <div className="pass-status">
          {evaluation.grade === 'A' || evaluation.grade === 'B' ? (
            <Alert
              message="✅ Analysis Quality Passed"
              type="success"
              showIcon
              icon={<CheckCircleOutlined />}
            />
          ) : (
            <Alert
              message="❌ Analysis Quality Needs Improvement"
              type="error"
              showIcon
              icon={<CloseCircleOutlined />}
            />
          )}
        </div>
      </div>

      <Divider />

      <div className="dimension-scores">
        <Title level={5}>Dimension Scores</Title>
        <div className="dimensions-list" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {Object.entries(evaluation.dimensions).map(([key, value]: [string, any]) => {
            const percentage = value.score
            const statusColor = percentage >= 80 ? '#52c41a' : percentage >= 60 ? '#1890ff' : '#ff4d4f'

            return (
              <div key={key} className="dimension-item" style={{
                padding: '20px',
                background: '#ffffff',
                borderRadius: '10px',
                border: '1px solid #f0f0f0',
                borderLeft: `3px solid ${statusColor}`
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#262626'
                  }}>
                    {dimensionNames[key] || key}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      fontSize: '24px',
                      fontWeight: '500',
                      color: statusColor
                    }}>
                      {value.score.toFixed(0)}
                    </div>
                    <div style={{
                      fontSize: '14px',
                      color: '#8c8c8c'
                    }}>
                      points
                    </div>
                    {value.score >= 80 ? (
                      <CheckCircleOutlined style={{ fontSize: '18px', color: '#52c41a' }} />
                    ) : value.score >= 60 ? (
                      <WarningOutlined style={{ fontSize: '18px', color: '#faad14' }} />
                    ) : (
                      <CloseCircleOutlined style={{ fontSize: '18px', color: '#ff4d4f' }} />
                    )}
                  </div>
                </div>

                {/* Progress Bar */}
                <div style={{
                  height: '6px',
                  background: '#f5f5f5',
                  borderRadius: '3px',
                  overflow: 'hidden',
                  marginBottom: '12px'
                }}>
                  <div style={{
                    width: `${percentage}%`,
                    height: '100%',
                    background: statusColor,
                    borderRadius: '3px',
                    transition: 'width 0.3s ease'
                  }} />
                </div>

                {/* Reasoning/Explanation */}
                {value.reasoning && (
                  <div style={{
                    fontSize: '13px',
                    color: '#595959',
                    lineHeight: '1.6',
                    padding: '12px',
                    background: '#fafafa',
                    borderRadius: '8px'
                  }}>
                    <div style={{
                      fontSize: '12px',
                      color: '#8c8c8c',
                      marginBottom: '6px',
                      fontWeight: '500'
                    }}>
                      💡 Score Reasoning:
                    </div>
                    {value.reasoning}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {evaluation.issues && evaluation.issues.length > 0 && (
        <>
          <Divider />
          <div className="issues-section">
            <Title level={5}>Issues Found ({evaluation.issues.length})</Title>
            <List
              size="small"
              dataSource={evaluation.issues}
              renderItem={(issue) => (
                <List.Item className="issue-item">
                  <Tag color="warning">Issue</Tag>
                  {issue}
                </List.Item>
              )}
            />
          </div>
        </>
      )}

      {evaluation.recommendations && evaluation.recommendations.length > 0 && (
        <>
          <Divider />
          <div className="recommendations-section">
            <Title level={5}>Improvement Suggestions ({evaluation.recommendations.length})</Title>
            <List
              size="small"
              dataSource={evaluation.recommendations}
              renderItem={(rec) => (
                <List.Item className="recommendation-item">
                  <Tag color="blue">Suggestion</Tag>
                  {rec}
                </List.Item>
              )}
            />
          </div>
        </>
      )}
    </Card>
  )
}

export default QualityReport