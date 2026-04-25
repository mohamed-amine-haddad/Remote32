const BASE = '/api/sessions/application'

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

export function apiGetApplicationSession(id) {
    return request(`/${id}`)
}

export function apiStartApplicationSession(body) {
    return request('', {
        method: 'POST',
        body: JSON.stringify(body),
    })
}

export function apiEndApplicationSession(id) {
    return request(`/${id}/end`, { method: 'POST' })
}

export function apiFlash(sessionId, elfFilename) {
    return request(`/${sessionId}/flash`, {
        method: 'POST',
        body: JSON.stringify({ elf_filename: elfFilename }),
    })
}

export function apiCommand(sessionId, uartCommand) {
    return request(`/${sessionId}/command`, {
        method: 'POST',
        body: JSON.stringify({ uart_command: uartCommand }),
    })
}

export function apiUartMessages(sessionId, sinceId = 0) {
    return request(`/${sessionId}/uart/messages?since_id=${sinceId}`)
}

export function apiUartSend(sessionId, text) {
    return request(`/${sessionId}/uart/send`, {
        method: 'POST',
        body: JSON.stringify({ text }),
    })
}
