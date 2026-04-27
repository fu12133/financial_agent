import React from 'react'
import { Layout as AntLayout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  BarChartOutlined,
  PieChartOutlined,
  MessageOutlined,
} from '@ant-design/icons'
import './Layout.css'

const { Header, Content, Footer } = AntLayout

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: 'Home' },
    { key: '/company', icon: <BarChartOutlined />, label: 'Company Analysis' },
    { key: '/industry', icon: <PieChartOutlined />, label: 'Industry Analysis' },
    { key: '/chat', icon: <MessageOutlined />, label: 'Intelligent Chat' },
  ]

  return (
    <AntLayout className="app-layout">
      <Header className="app-header">
        <div className="logo">
          <h1>🤖 Financial Analysis Agent</h1>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      <Content className="app-content">
        {children}
      </Content>
      <Footer className="app-footer">
        Financial Analysis AI Agent ©2024 | Powered by RAG + LLM
      </Footer>
    </AntLayout>
  )
}

export default Layout