import React from 'react'
import { Card, Progress, Alert, List, Tag, Divider } from 'antd'
import { CheckCircleOutlined, WarningOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { QualityEvaluation } from '../types'
import './QualityReport.css'

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
    <Card className="quality-report-card" title="📊 Quality Evaluation Report">
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
        <h4>Dimension Scores</h4>
        <div className="dimensions-grid">
          {Object.entries(evaluation.dimensions).map(([key, value]: [string, any]) => (
            <div key={key} className="dimension-item">
              <div className="dimension-name">{dimensionNames[key] || key}</div>
              <Progress
                percent={value.score}
                status={value.score >= 80 ? 'success' : value.score >= 60 ? 'normal' : 'exception'}
                size="small"
              />
              <div className="dimension-score-text">{value.score.toFixed(0)} points</div>
            </div>
          ))}
        </div>
      </div>

      {evaluation.issues && evaluation.issues.length > 0 && (
        <>
          <Divider />
          <div className="issues-section">
            <h4>
              <WarningOutlined style={{ color: '#faad14' }} /> Issues Found ({evaluation.issues.length})
            </h4>
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
            <h4>💡 Improvement Suggestions ({evaluation.recommendations.length})</h4>
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