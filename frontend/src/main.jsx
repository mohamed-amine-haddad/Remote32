import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DevicesPage from './pages/DevicesPage'
import ApplicationsPage from './pages/ApplicationsPage'
import DeviceDetailPage from './pages/DeviceDetailPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import DeviceSessionPage from './pages/DeviceSessionPage'
import ApplicationSessionPage from './pages/ApplicationSessionPage'
import ProfilePage from './pages/ProfilePage'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/devices" element={<DevicesPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/devices/:id" element={<DeviceDetailPage />} />
        <Route path="/applications/:id" element={<ApplicationDetailPage />} />
        <Route path="/session/device/:id" element={<DeviceSessionPage />} />
        <Route path="/session/application/:id" element={<ApplicationSessionPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)