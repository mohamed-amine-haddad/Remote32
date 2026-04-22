import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Navbar from '../components/Navbar'
import ControlDevicePanel from '../components/ControlDevicePanel'

// Mock data — will be replaced by GET /sessions/:id
const SESSION = {
    app_name: "Multi-Axis Motion Lab",
    status: "active",
    started_at: "14:32",
    ends_at: "15:32",
    time_left: "27:14",
    gdb_host: "retroboy",
    gdb_port: "3333",
    control_devices: [
        {
            device_id: "STM32-03",
            label: "X-Axis Motor",
            default_elf: "x_axis_pid.elf",
            available_elfs: [
                {
                    filename: "x_axis_pid.elf",
                    buttons: [
                        { label: "Start",      uart_command: "CMD_X_START"  },
                        { label: "Stop",       uart_command: "CMD_X_STOP"   },
                        { label: "Speed +10%", uart_command: "CMD_X_SPD_UP" },
                        { label: "Speed -10%", uart_command: "CMD_X_SPD_DN" },
                        { label: "Reverse",    uart_command: "CMD_X_REV"    },
                    ],
                },
                {
                    filename: "x_axis_open_loop.elf",
                    buttons: [
                        { label: "Run CW",    uart_command: "CMD_X_CW"    },
                        { label: "Run CCW",   uart_command: "CMD_X_CCW"   },
                        { label: "Full stop", uart_command: "CMD_X_ESTOP" },
                    ],
                },
            ],
        },
        {
            device_id: "STM32-04",
            label: "Y-Axis Motor",
            default_elf: "y_axis_pid.elf",
            available_elfs: [
                {
                    filename: "y_axis_pid.elf",
                    buttons: [
                        { label: "Start",      uart_command: "CMD_Y_START"  },
                        { label: "Stop",       uart_command: "CMD_Y_STOP"   },
                        { label: "Speed +10%", uart_command: "CMD_Y_SPD_UP" },
                        { label: "Speed -10%", uart_command: "CMD_Y_SPD_DN" },
                    ],
                },
                {
                    filename: "y_axis_step_mode.elf",
                    buttons: [
                        { label: "Step +1",  uart_command: "CMD_Y_STEP_P"  },
                        { label: "Step -1",  uart_command: "CMD_Y_STEP_N"  },
                        { label: "Step +10", uart_command: "CMD_Y_STEP_PP" },
                        { label: "Step -10", uart_command: "CMD_Y_STEP_NN" },
                        { label: "Home",     uart_command: "CMD_Y_HOME"    },
                    ],
                },
                {
                    filename: "y_axis_calibration.elf",
                    buttons: [
                        { label: "Cal start", uart_command: "CMD_Y_CAL_START" },
                        { label: "Cal stop",  uart_command: "CMD_Y_CAL_STOP"  },
                        { label: "Save",      uart_command: "CMD_Y_CAL_SAVE"  },
                    ],
                },
            ],
        },
        {
            device_id: "STM32-05",
            label: "Sensor Array",
            default_elf: "sensor_continuous.elf",
            available_elfs: [
                {
                    filename: "sensor_continuous.elf",
                    buttons: [
                        { label: "Start sampling", uart_command: "CMD_S_START" },
                        { label: "Stop sampling",  uart_command: "CMD_S_STOP"  },
                        { label: "Reset counters", uart_command: "CMD_S_RESET" },
                    ],
                },
                {
                    filename: "sensor_trigger.elf",
                    buttons: [
                        { label: "Trigger once",  uart_command: "CMD_S_TRIG"   },
                        { label: "Trigger burst", uart_command: "CMD_S_BURST"  },
                        { label: "Set threshold", uart_command: "CMD_S_THRESH" },
                        { label: "Read raw",      uart_command: "CMD_S_RAW"    },
                    ],
                },
            ],
        },
    ],
}

// ── Session status badge ───────────────────────────────────────────────────────

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

// ── ApplicationSessionPage ─────────────────────────────────────────────────────

export default function ApplicationSessionPage() {

    const { id } = useParams()
    const [activeTab, setActiveTab] = useState(0)

    // Layout
    const page    = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 px-6 md:px-8 py-8 pb-24 items-start"

    // Cards
    const card      = "border-2 border-black rounded-none shadow-nb p-6"
    const cardTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-5"

    // Session info grid
    const infoGrid  = "grid grid-cols-2 gap-y-4 text-sm"
    const infoLabel = "text-gray-400 font-medium"
    const infoValue = "font-bold text-navy"

    // Tab bar
    const tabBar    = "flex overflow-x-auto whitespace-nowrap border-b-2 border-black"
    const tabActive = [
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
    const bar     = "sticky bottom-0 z-10 bg-white border-t-2 border-black px-6 py-4 flex items-center justify-between"
    const endBtn  = [
        "px-5 py-3",
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

                {/* ── LEFT: Camera + Session info ───────────────── */}
                <div className="flex flex-col gap-6">

                    <Link
                        to={`/applications/${id}`}
                        className="text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2 w-fit"
                    >
                        ← Back to application
                    </Link>

                    {/* Camera feed */}
                    <div className={card}>
                        <p className={cardTitle}>Live Feed</p>
                        <div
                            className="relative w-full bg-gray-900 border-2 border-black"
                            style={{ aspectRatio: "16/9" }}
                        >
                            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-500 select-none">
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
                                    stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M23 7l-7 5 7 5V7z" />
                                    <rect x="1" y="5" width="15" height="14" rx="0" />
                                </svg>
                                <span className="text-xs font-medium">Camera stream — coming soon</span>
                            </div>
                        </div>
                    </div>

                    {/* Session info */}
                    <div className={card}>
                        <p className={cardTitle}>Session Info</p>
                        <div className={infoGrid}>
                            <span className={infoLabel}>Application</span>
                            <span className={infoValue}>{SESSION.app_name}</span>

                            <span className={infoLabel}>Status</span>
                            <span><SessionBadge status={SESSION.status} /></span>

                            <span className={infoLabel}>Started at</span>
                            <span className={infoValue}>{SESSION.started_at}</span>

                            <span className={infoLabel}>Ends at</span>
                            <span className={infoValue}>{SESSION.ends_at}</span>
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
                            <ConnectionRow label="Host" value={SESSION.gdb_host} />
                            <ConnectionRow label="Port" value={SESSION.gdb_port} />
                        </div>
                    </div>
                </div>

                {/* ── RIGHT: Control panel (tabbed) ─────────────── */}
                {/* Card without top padding so the tab bar is flush with the card border */}
                <div className="border-2 border-black rounded-none shadow-nb">

                    {/* Tab bar */}
                    <div className={tabBar}>
                        {SESSION.control_devices.map((device, i) => (
                            <button
                                key={device.device_id}
                                className={activeTab === i ? tabActive : tabInactive}
                                onClick={() => setActiveTab(i)}
                            >
                                {device.label}
                            </button>
                        ))}
                    </div>

                    {/* Panels — all rendered, inactive ones hidden via CSS.
                        This keeps each ControlDevicePanel mounted so its state
                        (firmware selection, command log) persists across tab switches. */}
                    {SESSION.control_devices.map((device, i) => (
                        <div key={device.device_id} className={activeTab !== i ? 'hidden' : 'p-6'}>
                            <ControlDevicePanel device={device} />
                        </div>
                    ))}
                </div>

            </main>

            {/* ── BOTTOM BAR ─────────────────────────────────────── */}
            <div className={bar}>
                <div className="flex items-center">
                    <span className="text-sm text-gray-500">Session ends in</span>
                    <span className="font-mono font-bold text-navy text-lg ml-2">
                        {SESSION.time_left}
                    </span>
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
