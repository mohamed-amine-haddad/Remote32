import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

// Wrap any <Route> that requires the user to be authenticated.
// While the initial /me check is still loading, render nothing to
// avoid a flash-redirect before we know the session status.
export default function ProtectedRoute({ children }) {
    const { user, loading } = useAuth()

    if (loading) return null
    if (!user) return <Navigate to="/login" replace />
    return children
}
