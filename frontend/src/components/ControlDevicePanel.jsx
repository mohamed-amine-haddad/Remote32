import { useState, useEffect, useRef } from 'react'

// ── ControlDevicePanel ────────────────────────────────────────────────────────
//
// Self-contained panel for one control device inside an application session.
// Each instance owns its own firmware selection and command log — switching
// tabs in ApplicationSessionPage does not reset another panel's state because
// all panels stay mounted (only visibility toggles).
//
// Props:
//   device — one element from SESSION.control_devices

export default function ControlDevicePanel({ device }) {

    const [selectedElf, setSelectedElf]   = useState(device.default_elf)
    const [commandLog,  setCommandLog]    = useState([])
    const [lastClicked, setLastClicked]   = useState(null)   // index of flashing button
    const [isFlashing,  setIsFlashing]    = useState(false)  // firmware flash in progress

    const logRef     = useRef(null)
    const mountedRef = useRef(false)   // skip the flash effect on first render

    // Auto-scroll the log to the latest entry whenever a new command is appended
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight
        }
    }, [commandLog])

    // Trigger "Flashing…" indicator when the user changes the firmware, but
    // not on the initial render (the board is already running default_elf)
    useEffect(() => {
        if (!mountedRef.current) {
            mountedRef.current = true
            return
        }
        console.log("flash:", selectedElf)
        setLastClicked(null)   // cancel any active button flash
        setIsFlashing(true)
        const timer = setTimeout(() => setIsFlashing(false), 2000)
        return () => clearTimeout(timer)
    }, [selectedElf])

    // Derive the button set from the currently selected elf filename
    const currentElf = device.available_elfs.find(e => e.filename === selectedElf)
    const buttons    = currentElf ? currentElf.buttons : []

    const handleCommand = (btn, index) => {
        console.log("uart:", btn.uart_command)
        const timestamp = new Date().toLocaleTimeString()
        setCommandLog(prev => [...prev, `[${timestamp}]  →  ${btn.uart_command}`])
        setLastClicked(index)
        setTimeout(() => setLastClicked(null), 500)
    }

    // ── Class strings ─────────────────────────────────────────────────────────

    const section    = "mb-5 pb-5 border-b border-gray-100 last:border-b-0 last:mb-0 last:pb-0"
    const label      = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-2 block"

    const select = [
        "w-full border-2 border-black rounded-none",
        "bg-white font-body text-sm px-3 py-2",
        "cursor-pointer focus:outline-none",
    ].join(" ")

    const flashNote  = "text-xs text-gray-400 mt-2"
    const flashingTxt = "text-xs font-bold text-accent mt-2 animate-pulse"

    const cmdBtn = [
        "bg-white border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-wide",
        "shadow-nb-sm py-3 px-4 cursor-pointer",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100",
    ].join(" ")

    const cmdBtnActive = [
        "bg-accent border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-wide",
        "shadow-nb-sm py-3 px-4 cursor-pointer",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100",
    ].join(" ")

    const log = [
        "h-36 overflow-y-auto",
        "border-2 border-black bg-gray-50 p-3",
    ].join(" ")

    return (
        <div>

            {/* ── SECTION 1: Firmware selector ─────────────────── */}
            <div className={section}>
                <label className={label}>Active firmware</label>
                <select
                    className={select}
                    value={selectedElf}
                    onChange={e => setSelectedElf(e.target.value)}
                >
                    {device.available_elfs.map(elf => (
                        <option key={elf.filename} value={elf.filename}>
                            {elf.filename}
                        </option>
                    ))}
                </select>
                {isFlashing
                    ? <p className={flashingTxt}>Flashing firmware…</p>
                    : <p className={flashNote}>Changing firmware reflashes the control board automatically.</p>
                }
            </div>

            {/* ── SECTION 2: Command buttons ───────────────────── */}
            <div className={section}>
                <p className={label}>Commands</p>
                {buttons.length > 0 ? (
                    <div className="grid grid-cols-2 gap-3">
                        {buttons.map((btn, i) => (
                            <button
                                key={btn.uart_command}
                                className={lastClicked === i ? cmdBtnActive : cmdBtn}
                                onClick={() => handleCommand(btn, i)}
                            >
                                {btn.label}
                            </button>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-gray-400 italic">No commands for this firmware.</p>
                )}
            </div>

            {/* ── SECTION 3: Command log ───────────────────────── */}
            <div>
                <p className={label}>Command log</p>
                <div className={log} ref={logRef}>
                    {commandLog.length === 0
                        ? (
                            <p className="text-xs text-gray-400 italic text-center mt-10">
                                No commands sent yet.
                            </p>
                        )
                        : commandLog.map((entry, i) => (
                            <p key={i} className="font-mono text-xs text-navy leading-5">
                                {entry}
                            </p>
                        ))
                    }
                </div>
            </div>

        </div>
    )
}
