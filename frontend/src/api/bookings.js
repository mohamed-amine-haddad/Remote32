const BASE = '/api/bookings'

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

export function apiListBookings(resourceType, resourceId) {
    const params = new URLSearchParams({
        resource_type: resourceType,
        resource_id: resourceId,
    })
    return request(`?${params}`)
}

export function apiCreateBooking(body) {
    return request('', {
        method: 'POST',
        body: JSON.stringify(body),
    })
}
