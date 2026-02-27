import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ToolPage from './pages/ToolPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import Dashboard from './pages/Dashboard'
import AnalyzerPage from './pages/AnalyzerPage'
import HistoryPage from './pages/HistoryPage'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import InsightsPage from './pages/InsightsPage'
import ProfilePage from './pages/ProfilePage'
import AuthGuard from './components/AuthGuard'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/tool" element={<Navigate to="/analyzer" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/dashboard" element={<AuthGuard><Dashboard /></AuthGuard>} />
        <Route path="/analyzer" element={<AuthGuard><AnalyzerPage /></AuthGuard>} />
        <Route path="/history" element={<AuthGuard><HistoryPage /></AuthGuard>} />
        <Route path="/projects" element={<AuthGuard><ProjectsPage /></AuthGuard>} />
        <Route path="/projects/:id" element={<AuthGuard><ProjectDetailPage /></AuthGuard>} />
        <Route path="/insights" element={<AuthGuard><InsightsPage /></AuthGuard>} />
        <Route path="/profile" element={<AuthGuard><ProfilePage /></AuthGuard>} />
      </Routes>
    </Router>
  )
}

export default App
