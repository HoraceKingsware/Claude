import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout'
import KnowledgeBasePage from './pages/KnowledgeBasePage'
import ChatPage from './pages/ChatPage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Navigate to="/knowledge-bases" replace />} />
        <Route path="knowledge-bases" element={<KnowledgeBasePage />} />
        <Route path="knowledge-bases/:kbId/chat" element={<ChatPage />} />
        <Route path="knowledge-bases/:kbId/graph" element={<KnowledgeGraphPage />} />
      </Route>
    </Routes>
  )
}

export default App
