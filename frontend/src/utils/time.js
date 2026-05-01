export function toDateStr(date) {
    const y = date.getFullYear()
    const m = String(date.getMonth() + 1).padStart(2, '0')
    const d = String(date.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
}

export function toMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number)
    return h * 60 + m
}

export function fromMinutes(mins) {
    const h = Math.floor(mins / 60).toString().padStart(2, '0')
    const m = (mins % 60).toString().padStart(2, '0')
    return `${h}:${m}`
}

export function hasConflict(reservations, startMins, durationMins) {
    const endMins = startMins + durationMins
    return reservations.some(r => {
        const rStart = toMinutes(r.start)
        const rEnd   = toMinutes(r.end)
        return startMins < rEnd && endMins > rStart
    })
}
