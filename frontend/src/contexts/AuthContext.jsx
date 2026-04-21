import { createContext, useContext, useEffect, useState } from 'react'
import { apiGetMe, apiLogin, apiLogout, apiRegister } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    // user: null  → not authenticated
    // user: {...} → authenticated (id, name, email, role)
    const [user, setUser] = useState(null)
    // loading: true while the initial /me check is in flight
    const [loading, setLoading] = useState(true)

    // On mount, ask the backend if there is a valid session cookie.
    // If yes, restore the user. If the cookie is missing or expired, /me
    // returns 401 and we stay logged out (no redirect here).
    useEffect(() => {
        apiGetMe()
            .then(setUser)
            .catch(() => setUser(null))
            .finally(() => setLoading(false))
    }, [])

    async function login(email, password, rememberMe) {
        const userData = await apiLogin(email, password, rememberMe)
        setUser(userData)
        return userData
    }

    async function register(name, email, password) {
        const userData = await apiRegister(name, email, password)
        // Registration does not issue a cookie; redirect to login after.
        return userData
    }

    async function logout() {
        await apiLogout()
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

// Convenience hook — import this in any component that needs auth state.
export function useAuth() {
    return useContext(AuthContext)
}
