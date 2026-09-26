import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/contexts/AuthContext'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { ToastProvider } from '@/components/common'
import { ProtectedRoute, PublicRoute, ErrorBoundary } from '@/components/common'

// Pages
import { Landing } from '@/pages/Landing'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Dashboard } from '@/pages/Dashboard'
import { Resumes } from '@/pages/Resumes'
import { ResumeAnalysis } from '@/pages/ResumeAnalysis'
import { InterviewSetup } from '@/pages/InterviewSetup'
import { Interview } from '@/pages/Interview'
import { InterviewResults } from '@/pages/InterviewResults'
import { Skills } from '@/pages/Skills'
import { Learning } from '@/pages/Learning'
import { InterviewHistory } from '@/pages/InterviewHistory'
import { Progress } from '@/pages/Progress'
import { Profile } from '@/pages/Profile'
import { Settings } from '@/pages/Settings'
import { JobDescriptions } from '@/pages/JobDescriptions'

import './styles/global.css'

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <ToastProvider>
            <Router>
              <div className="app">
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<PublicRoute><Landing /></PublicRoute>} />
                  <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
                  <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

                  {/* Protected routes */}
                  <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                  <Route path="/resumes" element={<ProtectedRoute><Resumes /></ProtectedRoute>} />
                  <Route path="/resumes/:id/analysis" element={<ProtectedRoute><ResumeAnalysis /></ProtectedRoute>} />
                  <Route path="/job-descriptions" element={<ProtectedRoute><JobDescriptions /></ProtectedRoute>} />
                  <Route path="/interview/setup" element={<ProtectedRoute><InterviewSetup /></ProtectedRoute>} />
                  <Route path="/interview/:id" element={<ProtectedRoute><Interview /></ProtectedRoute>} />
                  <Route path="/interview/:id/results" element={<ProtectedRoute><InterviewResults /></ProtectedRoute>} />
                  <Route path="/skills" element={<ProtectedRoute><Skills /></ProtectedRoute>} />
                  <Route path="/learning" element={<ProtectedRoute><Learning /></ProtectedRoute>} />
                  <Route path="/learning/resources" element={<ProtectedRoute><div className="p-8 text-center">Learning Resources - Coming Soon</div></ProtectedRoute>} />
                  <Route path="/interview-history" element={<ProtectedRoute><InterviewHistory /></ProtectedRoute>} />
                  <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
                  <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                  <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

                  {/* 404 */}
                  <Route path="*" element={<div className="p-8 text-center">404 - Page Not Found</div>} />
                </Routes>
              </div>
            </Router>
          </ToastProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App