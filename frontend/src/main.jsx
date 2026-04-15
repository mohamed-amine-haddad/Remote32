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
import DeviceDetailPage from './pages/DeviceDetailPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import BookingPage from './pages/BookingPage'
import DeviceSessionPage from './pages/DeviceSessionPage'
import ApplicationSessionPage from './pages/ApplicationSessionPage'
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
          <Route path="/applications" element={<ApplicationsPage />} />
          <Route path="/devices/:id" element={<DeviceDetailPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailPage />} />
          <Route path="/book/device/:id" element={<ProtectedRoute><BookingPage type="device" /></ProtectedRoute>} />
          <Route path="/book/application/:id" element={<ProtectedRoute><BookingPage type="application" /></ProtectedRoute>} />
          <Route path="/session/device/:id" element={<ProtectedRoute><DeviceSessionPage /></ProtectedRoute>} />
          <Route path="/session/application/:id" element={<ProtectedRoute><ApplicationSessionPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
)
