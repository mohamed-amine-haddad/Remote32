import { useState, useMemo, useEffect } from 'react'
import { apiListBookings } from '../api/bookings'
import { apiGetApplicationConfig } from '../api/applications'
import { toDateStr } from '../utils/time'

export function useBookingData(id) {
    const [config,       setConfig]       = useState(null)
    const [jsonPath,     setJsonPath]     = useState(null)
    const [reservations, setReservations] = useState([])
    const [loading,      setLoading]      = useState(true)
    const [selectedDay,  setSelectedDay]  = useState(new Date())
    const [duration,     setDuration]     = useState(null)

    useEffect(() => {
        apiGetApplicationConfig(id)
            .then(cfg => {
                setConfig(cfg)
                setJsonPath(cfg.json_path)
                setDuration(cfg.min_duration_minutes)
                return apiListBookings(cfg.json_path)
            })
            .then(setReservations)
            .catch(() => {})
            .finally(() => setLoading(false))
    }, [id])

    const dayReservations = useMemo(() => {
        const dateStr = toDateStr(selectedDay)
        return reservations.filter(r => r.date === dateStr)
    }, [selectedDay, reservations])

    const reservedDates = useMemo(() => {
        return new Set(reservations.map(r => r.date))
    }, [reservations])

    return {
        config, jsonPath,
        reservations, dayReservations, reservedDates,
        selectedDay, setSelectedDay,
        duration, setDuration,
        loading,
    }
}
