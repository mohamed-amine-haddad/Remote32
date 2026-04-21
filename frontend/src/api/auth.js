// All requests go through /api, which Vite proxies to http://localhost:8000 in dev.
// In production, nginx handles the same proxying.
// credentials: 'include' ensures the httpOnly cookie is sent with every request.

const BASE = '/api/auth'

async function request(path, options = {}) {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        ...options,
    })

    if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `HTTP ${res.status}`)
    }

    // 204 No Content or similar
    if (res.status === 204) return null
    return res.json()
}

export function apiRegister(name, email, password) {
    return request('/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
    })
}

export function apiLogin(email, password, remember_me) {
    return request('/login', {
        method: 'POST',
        body: JSON.stringify({ email, password, remember_me }),
    })
}

export function apiLogout() {
    return request('/logout', { method: 'POST' })
}

export function apiGetMe() {
    return request('/me')
}
