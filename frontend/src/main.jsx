import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DevicesPage from './pages/DevicesPage'
import ApplicationsPage from './pages/ApplicationsPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import BookingPage from './pages/BookingPage'
import SessionPage from './pages/SessionPage'
import ProfilePage from './pages/ProfilePage'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Browsable without auth — anyone can see what's available */}
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/devices/:id" element={<ApplicationDetailPage type="device" />} />
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailPage type="application" />} />
          <Route path="/book/device/:id" element={<ProtectedRoute><BookingPage type="device" /></ProtectedRoute>} />
          <Route path="/book/application/:id" element={<ProtectedRoute><BookingPage type="application" /></ProtectedRoute>} />
          <Route path="/session/device/:id"      element={<ProtectedRoute><SessionPage /></ProtectedRoute>} />
          <Route path="/session/application/:id" element={<ProtectedRoute><SessionPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
)
