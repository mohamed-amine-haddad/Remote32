import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import ControlDevicePanel from '../components/ControlDevicePanel'
import SerialMonitor from '../components/SerialMonitor'
import { apiGetApplicationSession, apiEndApplicationSession, apiFlash, apiCommand, apiGetCameraStream } from '../api/applicationSessions'

// ── CopyButton ─────────────────────────────────────────────────────────────────

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
    const row = "flex items-center justify-between py-3 border-b border-gray-200 last:border-b-0"
    const lbl = "text-xs font-bold uppercase tracking-widest text-gray-400 w-16 shrink-0"
    const val = "font-mono font-bold text-navy text-sm flex-1 ml-4"
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
    const wrap = "flex gap-4 py-4 border-b border-gray-100 last:border-b-0"
    const num  = [
        "w-7 h-7 shrink-0",
        "flex items-center justify-center",
        "border-2 border-black rounded-none",
        "bg-navy text-white text-xs font-bold",
    ].join(" ")

    return (
        <div className={wrap}>
            <span className={num}>{number}</span>
            <div className="flex flex-col gap-1">
                <p className="text-sm font-bold text-navy">{title}</p>
                <p className="text-sm text-gray-500 leading-relaxed">{description}</p>
            </div>
        </div>
    )
}

// ── SessionPage ────────────────────────────────────────────────────────────────
//
// Unified session page for all application types.
// The control panel (right column) only renders when the application has
// control devices. Applications with no control devices (formerly "devices")
// use the same page with a 2-column layout instead.

export default function SessionPage() {

    const { id } = useParams()
    const navigate = useNavigate()

    const [session,   setSession]   = useState(null)
    const [loading,   setLoading]   = useState(true)
    const [error,     setError]     = useState(null)
    const [ending,    setEnding]    = useState(false)
    const [activeTab, setActiveTab] = useState(0)
    const [cameraUrl, setCameraUrl] = useState(null)

    useEffect(() => {
        apiGetApplicationSession(id)
            .then(setSession)
            .catch(() => setSession(null))
            .finally(() => setLoading(false))

        apiGetCameraStream(id)
            .then(data => setCameraUrl(data.stream_url))
            .catch(() => setCameraUrl(""))
    }, [id])

    const hasControlDevices = (session?.control_devices?.length ?? 0) > 0
    const backPath = hasControlDevices ? '/applications' : '/devices'

    const handleEndSession = async () => {
        setEnding(true)
        setError(null)
        try {
            await apiEndApplicationSession(id)
            navigate(backPath)
        } catch (err) {
            setError(err.message)
            setEnding(false)
        }
    }

    // Layout
    const page    = "min-h-screen bg-white font-body flex flex-col"
    const content = hasControlDevices
        ? "flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 px-6 md:px-8 py-8 pb-6 items-start"
        : "flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 px-6 md:px-10 py-8 pb-6 items-start"

    // Cards
    const card      = "border-2 border-black rounded-none shadow-nb p-6"
    const cardTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-5"

    // Tab bar (control devices panel)
    const tabBar     = "flex overflow-x-auto whitespace-nowrap border-b-2 border-black"
    const tabActive  = [
        "px-4 py-3 shrink-0",
        "bg-navy text-white border-2 border-black",
        "font-bold text-xs uppercase tracking-widest",
        "cursor-pointer",
    ].join(" ")
    const tabInactive = [
        "px-4 py-3 shrink-0",
        "bg-white text-navy border-2 border-black",
        "font-bold text-xs uppercase tracking-widest",
        "hover:bg-accent transition-colors duration-100",
        "cursor-pointer",
    ].join(" ")

    // Bottom bar
    const bar    = "sticky bottom-0 z-10 bg-white border-t-2 border-black px-6 py-4 flex items-center justify-between"
    const endBtn = [
        "px-5 py-3",
        "bg-red-500 text-white border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest",
        "shadow-nb-sm",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100 cursor-pointer",
    ].join(" ")

    if (loading) return (
        <div className={page}>
            <Navbar />
            <div className="flex-1 px-6 py-8">
                <p className="text-sm text-gray-400 font-medium">Loading session…</p>
            </div>
        </div>
    )

    if (!session) return (
        <div className={page}>
            <Navbar />
            <div className="flex-1 px-6 py-8">
                <p className="text-lg font-bold text-red-500">Session not found.</p>
                <button
                    onClick={() => navigate(-1)}
                    className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2"
                >
                    ← Back
                </button>
            </div>
        </div>
    )

    return (
        <div className={page}>
            <Navbar />

            <main className={content}>

                {/* ── LEFT: Camera + Session info ───────────────── */}
                <div className="flex flex-col gap-6">

                    <Link
                        to={backPath}
                        className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2 w-fit"
                    >
                        ← Back to {hasControlDevices ? 'applications' : 'devices'}
                    </Link>

                    {/* Camera feed */}
                    <div className={card}>
                        <p className={cardTitle}>Live Feed</p>
                        <div
                            className="relative w-full bg-gray-900 border-2 border-black"
                            style={{ aspectRatio: "16/9" }}
                        >
                            {cameraUrl === null ? (
                                <div className="absolute inset-0 flex items-center justify-center text-gray-500 select-none">
                                    <span className="text-xs font-medium">Starting camera…</span>
                                </div>
                            ) : cameraUrl === "" ? (
                                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-500 select-none">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M23 7l-7 5 7 5V7z" />
                                        <rect x="1" y="5" width="15" height="14" rx="0" />
                                    </svg>
                                    <span className="text-xs font-medium">Camera unavailable</span>
                                </div>
                            ) : (
                                <img
                                    src={cameraUrl}
                                    alt="Live camera feed"
                                    className="w-full h-full object-contain"
                                    onError={() => setCameraUrl("")}
                                />
                            )}
                        </div>
                    </div>

                </div>

                {/* ── MIDDLE: GDB connection panel ──────────────── */}
                <div className={card}>
                    <p className={cardTitle}>Connect via STM32CubeIDE</p>

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

                    <div className="mt-6">
                        <p className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                            Connection details
                        </p>
                        <div className="border-2 border-black bg-gray-50 px-4">
                            <ConnectionRow label="Host" value={session.gdb_host} />
                            <ConnectionRow label="Port" value={session.gdb_port} />
                        </div>
                    </div>
                </div>

                {/* ── RIGHT: Control panel — only for applications with control devices ── */}
                {hasControlDevices && (
                    <div className="border-2 border-black rounded-none shadow-nb">

                        {/* Tab bar */}
                        <div className={tabBar}>
                            {session.control_devices.map((device, i) => (
                                <button
                                    key={device.device_id}
                                    className={activeTab === i ? tabActive : tabInactive}
                                    onClick={() => setActiveTab(i)}
                                >
                                    {device.label}
                                </button>
                            ))}
                        </div>

                        {/* Panels — all mounted, inactive ones hidden, so each panel's state survives tab switches */}
                        {session.control_devices.map((device, i) => (
                            <div key={device.device_id} className={activeTab !== i ? 'hidden' : 'p-6'}>
                                <ControlDevicePanel
                                    device={device}
                                    onFlash={elfFilename => apiFlash(id, elfFilename)}
                                    onCommand={uartCommand => apiCommand(id, uartCommand)}
                                />
                            </div>
                        ))}
                    </div>
                )}

            </main>

            {/* ── SERIAL MONITOR ─────────────────────────────────── */}
            <div className="px-6 md:px-8 pb-24">
                <SerialMonitor sessionId={id} />
            </div>

            {/* ── BOTTOM BAR ─────────────────────────────────────── */}
            <div className={bar}>
                <div className="flex items-center gap-6 text-sm flex-wrap">
                    <div>
                        <span className="text-gray-400 font-medium mr-2">Started</span>
                        <span className="font-mono font-bold text-navy">{session.started_at}</span>
                    </div>
                    <div>
                        <span className="text-gray-400 font-medium mr-2">Ends</span>
                        <span className="font-mono font-bold text-navy">{session.ends_at}</span>
                    </div>
                    <div>
                        <span className="text-gray-400 font-medium mr-2">Time left</span>
                        <span className="font-mono font-bold text-navy text-lg">{session.time_left}</span>
                    </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                    {error && <p className="text-xs font-medium text-red-600">{error}</p>}
                    <button
                        className={endBtn}
                        onClick={handleEndSession}
                        disabled={ending}
                    >
                        {ending ? 'Ending…' : 'End session'}
                    </button>
                </div>
            </div>
        </div>
    )
}
