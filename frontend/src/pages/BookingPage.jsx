import { useState, useMemo } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import Calendar from 'react-calendar'
import Navbar from '../components/Navbar'

// ── Mock config (will come from backend) ─────────────────────────────────────

const SESSION_CONFIG = {
    min_duration_minutes: 15,
    max_duration_minutes: 60,
    slot_step_minutes: 15,     // granularity of the timeline blocks
}

// Mock existing reservations — each has a date, start time, end time, status
// In production these come from GET /bookings?resource_id=X&date=Y
const MOCK_RESERVATIONS = [
    { date: '2026-04-10', start: '09:00', end: '10:00', status: 'reserved' },
    { date: '2026-04-10', start: '14:00', end: '14:30', status: 'occupied' },
    { date: '2026-04-11', start: '10:00', end: '11:00', status: 'reserved' },
    { date: '2026-04-13', start: '08:00', end: '09:00', status: 'occupied' },
]

// ── Helpers ───────────────────────────────────────────────────────────────────

// Format a Date object as "YYYY-MM-DD" for comparison with mock data
function toDateStr(date) {
    return date.toISOString().split('T')[0]
}

// Convert "HH:MM" string to minutes since midnight
function toMinutes(timeStr) {
    const [h, m] = timeStr.split(':').map(Number)
    return h * 60 + m
}

// Convert minutes since midnight back to "HH:MM"
function fromMinutes(mins) {
    const h = Math.floor(mins / 60).toString().padStart(2, '0')
    const m = (mins % 60).toString().padStart(2, '0')
    return `${h}:${m}`
}

// Lab is open 08:00 – 20:00 (720 minutes of usable day)
const DAY_START = 8 * 60   // 480
const DAY_END   = 20 * 60  // 1200
const DAY_SPAN  = DAY_END - DAY_START  // 720

// Given a list of reservations for a day, check if a proposed slot conflicts
function hasConflict(reservations, startMins, durationMins) {
    const endMins = startMins + durationMins
    return reservations.some(r => {
        const rStart = toMinutes(r.start)
        const rEnd   = toMinutes(r.end)
        // Overlap: proposed start < existing end AND proposed end > existing start
        return startMins < rEnd && endMins > rStart
    })
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function BookingPage({ type }) {

    const { id } = useParams()
    const navigate = useNavigate()

    const [selectedDay, setSelectedDay]       = useState(new Date())
    const [startTime, setStartTime]           = useState('09:00')
    const [duration, setDuration]             = useState(SESSION_CONFIG.min_duration_minutes)
    const [error, setError]                   = useState(null)
    const [success, setSuccess]               = useState(false)

    // Reservations for the currently selected day
    const dayReservations = useMemo(() => {
        const dateStr = toDateStr(selectedDay)
        return MOCK_RESERVATIONS.filter(r => r.date === dateStr)
    }, [selectedDay])

    // Which calendar days have ANY reservation — used to mark dots on the calendar
    const reservedDates = useMemo(() => {
        return new Set(MOCK_RESERVATIONS.map(r => r.date))
    }, [])

    // Duration options in steps of slot_step_minutes between min and max
    const durationOptions = useMemo(() => {
        const opts = []
        for (
            let m = SESSION_CONFIG.min_duration_minutes;
            m <= SESSION_CONFIG.max_duration_minutes;
            m += SESSION_CONFIG.slot_step_minutes
        ) {
            opts.push(m)
        }
        return opts
    }, [])

    const handleConfirm = () => {
        setError(null)

        const startMins = toMinutes(startTime)
        const endMins   = startMins + duration

        // Validate within lab hours
        if (startMins < DAY_START) {
            setError(`Sessions cannot start before ${fromMinutes(DAY_START)}.`)
            return
        }
        if (endMins > DAY_END) {
            setError(`Session would end at ${fromMinutes(endMins)}, after lab closing time (${fromMinutes(DAY_END)}).`)
            return
        }

        // Validate no conflict
        if (hasConflict(dayReservations, startMins, duration)) {
            setError('This time slot conflicts with an existing reservation. Please choose a different time.')
            return
        }

        // Validate not in the past
        const now = new Date()
        const proposed = new Date(selectedDay)
        proposed.setHours(Math.floor(startMins / 60), startMins % 60, 0, 0)
        if (proposed < now) {
            setError('You cannot book a slot in the past.')
            return
        }

        // Success — in production this calls POST /bookings
        setSuccess(true)
    }

    // Go back to the detail page after success
    const handleBackAfterSuccess = () => {
        navigate(`/${type}s/${id}`)
    }

    // ── Class strings ─────────────────────────────────────────────────────────

    const page    = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    const backLink   = "text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2 mb-4 inline-block"
    const heading    = "font-display text-5xl md:text-6xl text-navy mb-10"

    // Two-column layout on desktop: calendar left, timeline + form right
    const grid = "grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-8 items-start"

    const card = [
        "border-2 border-black rounded-none",
        "shadow-nb p-6",
    ].join(" ")

    const sectionTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-4"

    const confirmBtn = [
        "w-full py-3 mt-2",
        "bg-accent border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-navy",
        "shadow-nb",
        "hover:shadow-none hover:translate-x-1 hover:translate-y-1",
        "transition-all duration-100 cursor-pointer",
    ].join(" ")

    // ── Success state ─────────────────────────────────────────────────────────

    if (success) {
        return (
            <div className={page}>
                <Navbar />
                <div className={content}>
                    <div className="max-w-md">
                        <div className={[card, "border-green-500"].join(" ")}>
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
                                Back to device
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    // ── Main render ───────────────────────────────────────────────────────────

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                <Link
                    to={`/${type}s/${id}`}
                    className={backLink}
                >
                    ← Back to {type}
                </Link>

                <h1 className={heading}>Book a session</h1>

                <div className={grid}>

                    {/* ── LEFT: Calendar ───────────────────────── */}
                    <div className={card}>
                        <p className={sectionTitle}>Select a day</p>

                        {/* react-calendar is unstyled by default.
                            We override its classes via the classNames prop
                            and global CSS in index.css (see below) */}
                        <Calendar
                            onChange={setSelectedDay}
                            value={selectedDay}
                            minDate={new Date()}      // cannot book in the past
                            locale="en-US"
                            tileClassName={({ date }) => {
                                const dateStr = toDateStr(date)
                                // Add a marker class to days that have reservations
                                if (reservedDates.has(dateStr)) return 'has-reservation'
                                return null
                            }}
                        />

                        {/* Legend */}
                        <div className="flex flex-wrap gap-4 mt-6">
                            <LegendItem color="bg-red-400"   label="In use" />
                            <LegendItem color="bg-accent"    label="Reserved" />
                            <LegendItem color="bg-green-400" label="Free" />
                        </div>
                    </div>

                    {/* ── RIGHT: Timeline + Form ────────────────── */}
                    <div className="flex flex-col gap-6">

                        {/* Day timeline */}
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

                        {/* Booking form */}
                        <div className={card}>
                            <p className={sectionTitle}>Your reservation</p>

                            {/* Start time */}
                            <div className="mb-5">
                                <label className="text-xs font-bold uppercase tracking-widest text-navy block mb-1">
                                    Start time
                                </label>
                                <input
                                    type="time"
                                    value={startTime}
                                    min={fromMinutes(DAY_START)}
                                    max={fromMinutes(DAY_END)}
                                    onChange={e => {
                                        setStartTime(e.target.value)
                                        setError(null)
                                    }}
                                    className={[
                                        "px-4 py-3 border-2 border-black rounded-none",
                                        "font-body text-sm bg-white w-full",
                                        "focus:outline-none",
                                    ].join(" ")}
                                />
                            </div>

                            {/* Duration */}
                            <div className="mb-6">
                                <label className="text-xs font-bold uppercase tracking-widest text-navy block mb-3">
                                    Duration — {duration} minutes
                                </label>

                                {/* Visual duration selector — pill buttons for each step */}
                                <div className="flex flex-wrap gap-2">
                                    {durationOptions.map(opt => (
                                        <button
                                            key={opt}
                                            onClick={() => {
                                                setDuration(opt)
                                                setError(null)
                                            }}
                                            className={[
                                                "px-4 py-2 text-sm font-bold border-2 border-black rounded-none",
                                                "transition-all duration-100",
                                                duration === opt
                                                    ? "bg-navy text-white shadow-none translate-x-0.5 translate-y-0.5"
                                                    : "bg-white text-navy shadow-nb-sm hover:shadow-none hover:translate-x-0.75 hover:translate-y-0.75",
                                            ].join(" ")}
                                        >
                                            {opt}m
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Booking summary */}
                            <BookingSummary
                                day={selectedDay}
                                startTime={startTime}
                                duration={duration}
                            />

                            {/* Error message */}
                            {error && (
                                <div className={[
                                    "mt-4 px-4 py-3",
                                    "border-2 border-red-500 bg-red-50",
                                    "text-sm font-medium text-red-700",
                                ].join(" ")}>
                                    {error}
                                </div>
                            )}

                            <button
                                className={confirmBtn}
                                onClick={handleConfirm}
                            >
                                Confirm booking
                            </button>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    )
}

// ── DayTimeline ───────────────────────────────────────────────────────────────
// Visual bar showing the full lab day (08:00–20:00) with colored blocks
// for each reservation and a preview of the user's proposed slot

function DayTimeline({ reservations, startTime, duration }) {

    const startMins   = toMinutes(startTime)
    const endMins     = startMins + duration
    const isInBounds  = startMins >= DAY_START && endMins <= DAY_END

    // Convert a reservation to left% and width% on the bar
    const toPercent = (mins) => ((mins - DAY_START) / DAY_SPAN) * 100

    const statusColors = {
        reserved: 'bg-accent border-black',
        occupied: 'bg-red-400 border-black',
    }

    return (
        <div>
            {/* Time axis labels */}
            <div className="flex justify-between text-xs text-gray-400 mb-1 font-mono">
                <span>08:00</span>
                <span>12:00</span>
                <span>16:00</span>
                <span>20:00</span>
            </div>

            {/* The bar itself — position:relative so blocks are positioned inside it */}
            <div className="relative h-10 bg-green-100 border-2 border-black">

                {/* Existing reservation blocks */}
                {reservations.map((r, i) => {
                    const left  = toPercent(toMinutes(r.start))
                    const width = toPercent(toMinutes(r.end)) - left
                    return (
                        <div
                            key={i}
                            className={[
                                "absolute top-0 h-full border-r border-l",
                                statusColors[r.status] || 'bg-gray-400',
                            ].join(" ")}
                            style={{ left: `${left}%`, width: `${width}%` }}
                            title={`${r.start} – ${r.end} (${r.status})`}
                        />
                    )
                })}

                {/* User's proposed slot — shown as a semi-transparent navy overlay */}
                {isInBounds && (
                    <div
                        className="absolute top-0 h-full bg-navy opacity-50 border-l-2 border-r-2 border-navy"
                        style={{
                            left:  `${toPercent(startMins)}%`,
                            width: `${toPercent(endMins) - toPercent(startMins)}%`,
                        }}
                        title={`Your slot: ${startTime} – ${fromMinutes(endMins)}`}
                    />
                )}
            </div>

            {/* Tooltip hint */}
            <p className="text-xs text-gray-400 mt-2">
                Your proposed slot is shown in <span className="font-bold text-navy">dark blue</span>.
            </p>

            {/* List of existing reservations for the day */}
            {reservations.length > 0 && (
                <div className="mt-4 flex flex-col gap-2">
                    {reservations.map((r, i) => (
                        <div key={i} className="flex items-center gap-3 text-sm">
                            <span className={[
                                "w-2 h-2 rounded-full shrink-0",
                                r.status === 'occupied' ? 'bg-red-400' : 'bg-accent',
                            ].join(" ")} />
                            <span className="font-mono text-navy">{r.start} – {r.end}</span>
                            <span className="text-gray-400 capitalize">{r.status}</span>
                        </div>
                    ))}
                </div>
            )}

            {reservations.length === 0 && (
                <p className="text-sm text-green-600 font-medium mt-3">
                    No reservations on this day — fully available.
                </p>
            )}
        </div>
    )
}

// ── BookingSummary ────────────────────────────────────────────────────────────
// Shows a clear human-readable summary of what will be booked

function BookingSummary({ day, startTime, duration }) {

    const startMins = toMinutes(startTime)
    const endTime   = fromMinutes(startMins + duration)

    return (
        <div className={[
            "border-2 border-black rounded-none p-4 mb-4",
            "bg-gray-50",
        ].join(" ")}>
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                Summary
            </p>
            <div className="grid grid-cols-2 gap-y-2 text-sm">
                <span className="text-gray-500">Date</span>
                <span className="font-bold text-navy">{day.toDateString()}</span>
                <span className="text-gray-500">From</span>
                <span className="font-bold text-navy">{startTime}</span>
                <span className="text-gray-500">To</span>
                <span className="font-bold text-navy">{endTime}</span>
                <span className="text-gray-500">Duration</span>
                <span className="font-bold text-navy">{duration} minutes</span>
            </div>
        </div>
    )
}

// ── LegendItem ────────────────────────────────────────────────────────────────

function LegendItem({ color, label }) {
    return (
        <div className="flex items-center gap-2 text-xs text-gray-600">
            <span className={`w-3 h-3 border border-black ${color}`} />
            {label}
        </div>
    )
}