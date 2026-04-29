import { useState, useEffect, useRef } from 'react'
import { apiUartMessages, apiUartSend } from '../api/applicationSessions'

const POLL_MS = 2000

export default function SerialMonitor({ sessionId }) {
    const [messages, setMessages] = useState([])
    const [input,    setInput]    = useState('')
    const [sending,  setSending]  = useState(false)
    const lastIdRef = useRef(0)
    const logRef    = useRef(null)

    useEffect(() => {
        let active = true

        async function poll() {
            if (!active) return
            try {
                const data = await apiUartMessages(sessionId, lastIdRef.current)
                if (active && data.messages.length > 0) {
                    lastIdRef.current = data.messages.at(-1).id
                    setMessages(prev => [...prev, ...data.messages])
                }
            } catch (_) {}
            if (active) setTimeout(poll, POLL_MS)
        }

        poll()
        return () => { active = false }
    }, [sessionId])

    useEffect(() => {
        if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
    }, [messages])

    async function handleSend() {
        const text = input.trim()
        if (!text || sending) return
        setSending(true)
        setInput('')
        try { await apiUartSend(sessionId, text) } catch (_) {}
        setSending(false)
    }

    function handleKeyDown(e) {
        if (e.key === 'Enter') handleSend()
    }

    function handleClear() {
        setMessages([])
        // lastIdRef.current stays at its current value — old messages won't reappear on next poll
    }

    // ── Styles ─────────────────────────────────────────────────────────────────

    const wrap  = "border-2 border-black rounded-none shadow-nb"
    const hdr   = "px-6 py-3 border-b-2 border-black flex items-center justify-between bg-white"
    const title = "text-xs font-bold uppercase tracking-widest text-gray-400"
    const clrbtn = [
        "text-xs font-bold uppercase tracking-widest",
        "text-gray-400 hover:text-black",
        "underline underline-offset-2 cursor-pointer",
    ].join(' ')
    const log = [
        "h-48 overflow-y-auto",
        "bg-gray-950 font-mono text-xs",
        "px-4 py-3 space-y-0.5",
    ].join(' ')
    const irow   = "flex border-t-2 border-black"
    const ifield = [
        "flex-1 font-mono text-sm px-4 py-3 bg-white",
        "border-none outline-none placeholder-gray-400",
    ].join(' ')
    const sbtn = [
        "shrink-0 px-5 py-3",
        "bg-navy text-white border-l-2 border-black",
        "font-bold text-xs uppercase tracking-widest",
        "hover:bg-accent hover:text-navy transition-colors duration-100 cursor-pointer",
        "disabled:opacity-40 disabled:cursor-not-allowed",
    ].join(' ')

    return (
        <div className={wrap}>

            <div className={hdr}>
                <span className={title}>Serial Monitor — Target Board UART</span>
                <button className={clrbtn} onClick={handleClear}>Clear</button>
            </div>

            <div ref={logRef} className={log}>
                {messages.length === 0 && (
                    <span className="text-gray-600">Waiting for data…</span>
                )}
                {messages.map(msg => (
                    <div key={msg.id} className="flex gap-2 leading-5">
                        <span className="text-gray-600 shrink-0">{msg.timestamp}</span>
                        <span className={msg.direction === 'tx' ? 'text-accent shrink-0' : 'text-green-400 shrink-0'}>
                            {msg.direction === 'tx' ? '→' : '←'}
                        </span>
                        <span className={msg.direction === 'tx' ? 'text-accent' : 'text-green-400'}>
                            {msg.text}
                        </span>
                    </div>
                ))}
            </div>

            <div className={irow}>
                <input
                    className={ifield}
                    placeholder="Type a command and press Enter…"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={sending}
                />
                <button
                    className={sbtn}
                    onClick={handleSend}
                    disabled={sending || !input.trim()}
                >
                    {sending ? 'Sending…' : 'Send'}
                </button>
            </div>

        </div>
    )
}
