import { toMinutes, fromMinutes } from '../utils/time'

const DAY_START = 0
const DAY_END   = 24 * 60
const DAY_SPAN  = 24 * 60

// "00:00", "02:00", ..., "22:00", "00:00" — 13 labels, one every 2 hours
const AXIS_LABELS = Array.from({ length: 13 }, (_, i) => String((i * 2) % 24).padStart(2, '0'))

const statusColors = {
    reserved: 'bg-accent border-black',
    occupied: 'bg-red-400 border-black',
}

export default function DayTimeline({ reservations, startTime, duration }) {
    const startMins  = toMinutes(startTime)
    const endMins    = startMins + duration
    const isInBounds = startMins >= DAY_START && endMins <= DAY_END

    const toPercent = (mins) => (mins / DAY_SPAN) * 100

    return (
        <div>
            {/* Time axis */}
            <div className="flex justify-between text-xs text-gray-400 mb-1 font-mono">
                {AXIS_LABELS.map((label, i) => (
                    <span key={i}>{label}</span>
                ))}
            </div>

            {/* Timeline bar */}
            <div className="relative h-10 bg-green-100 border-2 border-black">

                {reservations.map((r, i) => {
                    const left  = toPercent(toMinutes(r.start))
                    const width = toPercent(toMinutes(r.end)) - left
                    return (
                        <div
                            key={i}
                            className={[
                                "absolute top-0 h-full border-r border-l",
                                statusColors[r.status] || 'bg-gray-400 border-black',
                            ].join(" ")}
                            style={{ left: `${left}%`, width: `${width}%` }}
                            title={`${r.start} – ${r.end} (${r.status})`}
                        />
                    )
                })}

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

            <p className="text-xs text-gray-400 mt-2">
                Your proposed slot is shown in <span className="font-bold text-navy">dark blue</span>.
            </p>

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
