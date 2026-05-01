import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import Calendar from 'react-calendar'
import Navbar from '../components/Navbar'
import DayTimeline from '../components/DayTimeline'
import BookingSummary from '../components/BookingSummary'
import { useBookingData } from '../hooks/useBookingData'
import { apiCreateBooking } from '../api/bookings'
import { toDateStr, toMinutes, fromMinutes, hasConflict } from '../utils/time'

// Lab open hours — used for booking validation (separate from the 24h timeline display)
const LAB_OPEN  = 8  * 60   // 08:00
const LAB_CLOSE = 20 * 60   // 20:00

export default function BookingPage({ type }) {
    const { id } = useParams()
    const navigate = useNavigate()

    const {
        config, jsonPath,
        dayReservations, reservedDates,
        selectedDay, setSelectedDay,
        duration, setDuration,
        loading,
    } = useBookingData(id)

    const [startTime,  setStartTime]  = useState('09:00')
    const [error,      setError]      = useState(null)
    const [success,    setSuccess]    = useState(false)
    const [submitting, setSubmitting] = useState(false)

    const handleConfirm = async () => {
        setError(null)

        const startMins = toMinutes(startTime)
        const endMins   = startMins + duration

        if (startMins < LAB_OPEN) {
            setError(`Sessions cannot start before ${fromMinutes(LAB_OPEN)}.`)
            return
        }
        if (endMins > LAB_CLOSE) {
            setError(`Session would end at ${fromMinutes(endMins)}, after lab closing time (${fromMinutes(LAB_CLOSE)}).`)
            return
        }
        if (hasConflict(dayReservations, startMins, duration)) {
            setError('This time slot conflicts with an existing reservation. Please choose a different time.')
            return
        }

        const now = new Date()
        const proposed = new Date(selectedDay)
        proposed.setHours(Math.floor(startMins / 60), startMins % 60, 0, 0)
        if (proposed < now) {
            setError('You cannot book a slot in the past.')
            return
        }

        setSubmitting(true)
        try {
            await apiCreateBooking({
                json_path:        jsonPath,
                start_time:       `${toDateStr(selectedDay)}T${startTime}:00`,
                duration_minutes: duration,
            })
            setSuccess(true)
        } catch (err) {
            setError(err.message)
        } finally {
            setSubmitting(false)
        }
    }

    const handleBackAfterSuccess = () => navigate(`/${type}s/${id}`)

    // ── Class strings ──────────────────────────────────────────────────────────

    const page    = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    const backLink = "text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2 mb-4 inline-block"
    const heading  = "font-display text-5xl md:text-6xl text-navy mb-10"

    const card = "border-2 border-black rounded-none shadow-nb p-6"

    const sectionTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-4"

    const confirmBtn = [
        "w-full py-3 mt-2",
        "bg-accent border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-navy",
        "shadow-nb",
        "hover:shadow-none hover:translate-x-1 hover:translate-y-1",
        "transition-all duration-100 cursor-pointer",
    ].join(" ")

    // ── Loading ────────────────────────────────────────────────────────────────

    if (loading) return (
        <div className={page}>
            <Navbar />
            <div className={content}>
                <p className="text-sm text-gray-400 font-medium">Loading…</p>
            </div>
        </div>
    )

    // ── Success ────────────────────────────────────────────────────────────────

    if (success) return (
        <div className={page}>
            <Navbar />
            <div className={content}>
                <div className="max-w-md">
                    <div className={`${card} border-green-500`}>
                        <p className="font-display text-4xl text-navy mb-2">Booking confirmed</p>
                        <p className="text-sm text-gray-600 mb-1">
                            <span className="font-bold">Date:</span> {selectedDay.toDateString()}
                        </p>
                        <p className="text-sm text-gray-600 mb-1">
                            <span className="font-bold">Start:</span> {startTime}
                        </p>
                        <p className="text-sm text-gray-600 mb-6">
                            <span className="font-bold">Duration:</span> {duration} minutes
                        </p>
                        <button className={confirmBtn} onClick={handleBackAfterSuccess}>
                            Back to {type}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )

    // ── Main render ────────────────────────────────────────────────────────────

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                <Link to={`/${type}s/${id}`} className={backLink}>
                    ← Back to {type}
                </Link>

                <h1 className={heading}>Book a session</h1>

                {/* ── Top row: Calendar (left) | Form (right) — same height ───── */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch mb-8">

                    {/* Calendar */}
                    <div className={`${card} h-full`}>
                        <p className={sectionTitle}>Select a day</p>
                        <Calendar
                            onChange={setSelectedDay}
                            value={selectedDay}
                            minDate={new Date()}
                            locale="en-US"
                            tileClassName={({ date }) => {
                                const dateStr = toDateStr(date)
                                return reservedDates.has(dateStr) ? 'has-reservation' : null
                            }}
                        />
                        <div className="flex flex-wrap gap-4 mt-6">
                            <LegendItem color="bg-red-400"   label="In use" />
                            <LegendItem color="bg-accent"    label="Reserved" />
                            <LegendItem color="bg-green-400" label="Free" />
                        </div>
                    </div>

                    {/* Booking form */}
                    <div className={`${card} h-full`}>
                        <p className={sectionTitle}>Your reservation</p>

                        {/* Start time */}
                        <div className="mb-5">
                            <label className="text-xs font-bold uppercase tracking-widest text-navy block mb-1">
                                Start time
                            </label>
                            <input
                                type="time"
                                value={startTime}
                                onChange={e => { setStartTime(e.target.value); setError(null) }}
                                className="px-4 py-3 border-2 border-black rounded-none font-body text-sm bg-white w-full focus:outline-none"
                            />
                        </div>

                        {/* Duration slider */}
                        <div className="mb-6">
                            <label className="text-xs font-bold uppercase tracking-widest text-navy block mb-3">
                                Duration — {duration} minutes
                            </label>
                            <input
                                type="range"
                                min={config.min_duration_minutes}
                                max={config.max_duration_minutes}
                                step={config.slot_step_minutes}
                                value={duration}
                                onChange={e => { setDuration(Number(e.target.value)); setError(null) }}
                                className="booking-slider w-full"
                            />
                            <div className="flex justify-between text-xs text-gray-400 mt-1 font-mono">
                                <span>{config.min_duration_minutes}m</span>
                                <span>{config.max_duration_minutes}m</span>
                            </div>
                        </div>

                        <BookingSummary day={selectedDay} startTime={startTime} duration={duration} />

                        {error && (
                            <div className="mt-4 px-4 py-3 border-2 border-red-500 bg-red-50 text-sm font-medium text-red-700">
                                {error}
                            </div>
                        )}

                        <button
                            className={confirmBtn}
                            onClick={handleConfirm}
                            disabled={submitting}
                        >
                            {submitting ? 'Booking…' : 'Confirm booking'}
                        </button>
                    </div>

                </div>

                {/* ── Day timeline — full width below ───────────────────────────── */}
                <div className={card}>
                    <p className={sectionTitle}>
                        Schedule for {selectedDay.toDateString()}
                    </p>
                    <DayTimeline
                        reservations={dayReservations}
                        startTime={startTime}
                        duration={duration}
                    />
                </div>

            </div>
        </div>
    )
}

function LegendItem({ color, label }) {
    return (
        <div className="flex items-center gap-2 text-xs text-gray-600">
            <span className={`w-3 h-3 border border-black ${color}`} />
            {label}
        </div>
    )
}
