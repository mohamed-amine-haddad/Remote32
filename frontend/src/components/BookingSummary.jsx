import { toMinutes, fromMinutes } from '../utils/time'

export default function BookingSummary({ day, startTime, duration }) {
    const endTime = fromMinutes(toMinutes(startTime) + duration)

    return (
        <div className="border-2 border-black rounded-none p-4 mb-4 bg-gray-50">
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
