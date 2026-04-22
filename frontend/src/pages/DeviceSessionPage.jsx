import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'

// Mock data — will be replaced by GET /sessions/:id
const SESSION = {
    device_name: "STM32-01",
    status: "active",
    started_at: "14:32",
    time_left: "27:14",
    ends_at: "15:00",
    gdb_host: "retroboy",
    gdb_port: "3333",
}

// ── Session status badge ───────────────────────────────────────────────────────
// Separate from StatusBadge (which handles device availability).
// Session lifecycle statuses need their own color mapping.

const sessionBadgeColors = {
    active:    "bg-green-400 text-black",
    reserved:  "bg-accent text-navy",
    ended:     "bg-gray-200 text-gray-600",
    cancelled: "bg-red-400 text-white",
}

const sessionBadgeLabels = {
    active:    "Active",
    reserved:  "Reserved",
    ended:     "Ended",
    cancelled: "Cancelled",
}

function SessionBadge({ status }) {
    const base = [
        "inline-block px-2 py-1",
        "text-xs font-bold uppercase tracking-widest",
        "border border-black rounded-none",
    ].join(" ")
    return (
        <span className={`${base} ${sessionBadgeColors[status] ?? "bg-gray-100 text-gray-700"}`}>
            {sessionBadgeLabels[status] ?? status}
        </span>
    )
}

// ── CopyButton ─────────────────────────────────────────────────────────────────
// Copies `value` to clipboard; shows ✓ for 1.5 s then resets.

function CopyButton({ value }) {
    const [copied, setCopied] = useState(false)

    const handleCopy = () => {
        navigator.clipboard.writeText(value)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
    }

    const btn = [
        "w-8 h-8 shrink-0",
        "flex items-center justify-center",
        "border-2 border-black rounded-none",
        "text-sm font-bold",
        "hover:bg-black hover:text-white",
        "transition-colors duration-100 cursor-pointer",
    ].join(" ")

    return (
        <button className={btn} onClick={handleCopy} title="Copy to clipboard">
            {copied ? "✓" : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="0" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
            )}
        </button>
    )
}

// ── ConnectionRow ──────────────────────────────────────────────────────────────

function ConnectionRow({ label, value }) {
    const row   = "flex items-center justify-between py-3 border-b border-gray-200 last:border-b-0"
    const lbl   = "text-xs font-bold uppercase tracking-widest text-gray-400 w-16 shrink-0"
    const val   = "font-mono font-bold text-navy text-sm flex-1 ml-4"

    return (
        <div className={row}>
            <span className={lbl}>{label}</span>
            <span className={val}>{value}</span>
            <CopyButton value={value} />
        </div>
    )
}

// ── StepRow ────────────────────────────────────────────────────────────────────

function StepRow({ number, title, description }) {
    const wrap  = "flex gap-4 py-4 border-b border-gray-100 last:border-b-0"
    const num   = [
        "w-7 h-7 shrink-0",
        "flex items-center justify-center",
        "border-2 border-black rounded-none",
        "bg-navy text-white text-xs font-bold",
    ].join(" ")
    const body  = "flex flex-col gap-1"
    const ttl   = "text-sm font-bold text-navy"
    const desc  = "text-sm text-gray-500 leading-relaxed"

    return (
        <div className={wrap}>
            <span className={num}>{number}</span>
            <div className={body}>
                <p className={ttl}>{title}</p>
                <p className={desc}>{description}</p>
            </div>
        </div>
    )
}

// ── DeviceSessionPage ──────────────────────────────────────────────────────────

export default function DeviceSessionPage() {

    const { id } = useParams()

    // Layout
    const page    = "min-h-screen bg-white font-body flex flex-col"
    // pb-24 prevents the sticky bottom bar from covering the last card
    const content = "flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 px-6 md:px-10 py-8 pb-24 items-start"

    // Shared card style
    const card      = "border-2 border-black rounded-none shadow-nb p-6"
    const cardTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-5"

    // Session info grid rows
    const infoGrid  = "grid grid-cols-2 gap-y-4 text-sm"
    const infoLabel = "text-gray-400 font-medium"
    const infoValue = "font-bold text-navy"

    // Bottom bar
    const bar       = "sticky bottom-0 z-10 bg-white border-t-2 border-black px-6 py-4 flex items-center justify-between"
    const barLabel  = "text-sm text-gray-500"
    const barTimer  = "font-mono font-bold text-navy text-lg ml-2"

    const endBtn = [
        "px-5 py-2",
        "bg-red-500 text-white border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest",
        "shadow-nb-sm",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100 cursor-pointer",
    ].join(" ")

    return (
        <div className={page}>
            <Navbar />

            <main className={content}>

                {/* ── LEFT COLUMN ────────────────────────────────── */}
                <div className="flex flex-col gap-6">

                    {/* Back link */}
                    <Link
                        to={`/devices/${id}`}
                        className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2 w-fit"
                    >
                        ← Back to device
                    </Link>

                    {/* Camera feed card */}
                    <div className={card}>
                        <p className={cardTitle}>Live Feed</p>
                        {/* 16:9 aspect ratio placeholder — replaced by <img> pointing to nginx MJPEG stream */}
                        <div className="relative w-full bg-gray-900 border-2 border-black" style={{ aspectRatio: "16/9" }}>
                            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-500 select-none">
                                {/* Camera icon */}
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                                    stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M23 7l-7 5 7 5V7z" />
                                    <rect x="1" y="5" width="15" height="14" rx="0" />
                                </svg>
                                <span className="text-xs font-medium">Camera stream — coming soon</span>
                            </div>
                        </div>
                    </div>

                    {/* Session info card */}
                    <div className={card}>
                        <p className={cardTitle}>Session Info</p>
                        <div className={infoGrid}>

                            <span className={infoLabel}>Device</span>
                            <span className={infoValue}>{SESSION.device_name}</span>

                            <span className={infoLabel}>Status</span>
                            <span><SessionBadge status={SESSION.status} /></span>

                            <span className={infoLabel}>Started at</span>
                            <span className={infoValue}>{SESSION.started_at}</span>

                            <span className={infoLabel}>Ends at</span>
                            <span className={infoValue}>{SESSION.ends_at}</span>

                        </div>
                    </div>
                </div>

                {/* ── RIGHT COLUMN ───────────────────────────────── */}
                <div className={card}>
                    <p className={cardTitle}>Connect via STM32CubeIDE</p>

                    {/* Numbered steps */}
                    <StepRow
                        number={1}
                        title="Open Debug Configurations"
                        description="In STM32CubeIDE, go to Run → Debug Configurations → GDB Hardware Debugging."
                    />
                    <StepRow
                        number={2}
                        title="Set the remote target"
                        description="Under the Debugger tab, set the connection to Remote. Enter the host and port below."
                    />
                    <StepRow
                        number={3}
                        title="Connect and flash"
                        description="Click Debug. STM32CubeIDE will connect, flash your binary, and start the debug session."
                    />

                    {/* Connection details */}
                    <div className="mt-6">
                        <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                            Connection details
                        </p>
                        <div className="border-2 border-black bg-gray-50 px-4">
                            <ConnectionRow label="Host" value={SESSION.gdb_host} />
                            <ConnectionRow label="Port" value={SESSION.gdb_port} />
                        </div>
                    </div>
                </div>

            </main>

            {/* ── BOTTOM BAR ─────────────────────────────────────── */}
            <div className={bar}>
                <div className="flex items-center">
                    <span className={barLabel}>Session ends in</span>
                    <span className={barTimer}>{SESSION.time_left}</span>
                </div>
                <button
                    className={endBtn}
                    onClick={() => console.log("end session")}
                >
                    End session
                </button>
            </div>
        </div>
    )
}
