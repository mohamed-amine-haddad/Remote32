const BASE = '/api/sessions/device'

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

    if (res.status === 204) return null
    return res.json()
}

export function apiGetDeviceSession(id) {
    return request(`/${id}`)
}

export function apiStartDeviceSession(boardId) {
    return request('', {
        method: 'POST',
        body: JSON.stringify({ board_id: boardId }),
    })
}

export function apiEndDeviceSession(id) {
    return request(`/${id}/end`, { method: 'POST' })
}
