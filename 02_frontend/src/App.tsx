import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import CompanyAnalysis from './pages/CompanyAnalysis'
import IndustryAnalysis from './pages/IndustryAnalysis'
import Chat from './pages/Chat'
import './App.css'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/company" element={<CompanyAnalysis />} />
          <Route path="/industry" element={<IndustryAnalysis />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App