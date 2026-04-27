import React from 'react'
import { List, Card, Tag, Typography } from 'antd'
import { LinkOutlined, CalendarOutlined } from '@ant-design/icons'
import { NewsItem } from '../types'
import dayjs from 'dayjs'
import './NewsList.css'

const { Title, Paragraph, Text } = Typography

interface NewsListProps {
  news: NewsItem[]
  title?: string
}

const NewsList: React.FC<NewsListProps> = ({ news, title = '相关新闻' }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'green'
      case 'negative':
        return 'red'
      default:
        return 'default'
    }
  }

  return (
    <Card className="news-list-card" title={`📰 ${title}`}>
      <List
        itemLayout="vertical"
        dataSource={news}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            extra={
              item.url && (
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  <LinkOutlined /> 阅读原文
                </a>
              )
            }
          >
            <List.Item.Meta
              title={
                <div className="news-header">
                  <Text strong className="news-headline">
                    {item.headline}
                  </Text>
                  <div className="news-tags">
                    <Tag color={getSentimentColor(item.sentiment_polarity)}>
                      {item.sentiment_polarity}
                    </Tag>
                    {item.event_type && <Tag>{item.event_type}</Tag>}
                    {item.industry && <Tag color="blue">{item.industry}</Tag>}
                  </div>
                </div>
              }
              description={
                <div className="news-meta">
                  <CalendarOutlined />{' '}
                  {dayjs.unix(item.publish_time).format('YYYY-MM-DD HH:mm')}
                  {item.source && ` | 来源: ${item.source}`}
                </div>
              }
            />
            {item.summary && (
              <Paragraph ellipsis={{ rows: 3 }} className="news-summary">
                {item.summary}
              </Paragraph>
            )}
          </List.Item>
        )}
      />
    </Card>
  )
}

export default NewsList