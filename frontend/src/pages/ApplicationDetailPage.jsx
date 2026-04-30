import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import JsonRenderer from '../components/JsonRenderer'
import { useAuth } from '../contexts/AuthContext'
import { apiGetApplication } from '../api/applications'
import { apiStartApplicationSession } from '../api/applicationSessions'

// Used for both /devices/:id (type="device") and /applications/:id (type="application").
// The type prop controls the back link and booking destination only — data fetching is
// always through /api/applications since devices are applications with no control boards.
export default function ApplicationDetailPage({ type = "application" }) {

    const { id } = useParams()
    const navigate = useNavigate()
    const { user } = useAuth()
    const [application, setApplication] = useState(null)
    const [loading, setLoading] = useState(true)
    const [starting, setStarting] = useState(false)
    const [startError, setStartError] = useState(null)

    const backPath = `/${type}s`

    useEffect(() => {
        apiGetApplication(id)
            .then(setApplication)
            .catch(() => setApplication(null))
            .finally(() => setLoading(false))
    }, [id])

    async function handleStartSession() {
        if (!user) { navigate('/login'); return }
        setStarting(true)
        setStartError(null)
        try {
            const session = await apiStartApplicationSession({ json_path: application.json_path })
            navigate(`/session/${type}/${session.id}`)
        } catch (err) {
            setStartError(err.message)
            setStarting(false)
        }
    }

    const page = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    const header = "flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-10"
    const titleBlock = "flex flex-col gap-2"
    const heading = "font-display text-5xl md:text-6xl text-navy"
    const backLink = "text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2"

    const actions = "flex flex-wrap gap-3"

    const primaryBtn = [
        "px-5 py-3",
        "bg-accent border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-navy",
        "shadow-nb-sm",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100",
    ].join(" ")

    const secondaryBtn = [
        "px-5 py-3",
        "bg-white border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-navy",
        "shadow-nb-sm",
        "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
        "transition-all duration-100",
    ].join(" ")

    const card = [
        "border-2 border-black rounded-none",
        "shadow-nb p-6 md:p-8",
    ].join(" ")

    const cardTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-6"

    if (loading) return (
        <div className={page}>
            <Navbar />
            <div className={content}>
                <p className="text-sm text-gray-400 font-medium">Loading…</p>
            </div>
        </div>
    )

    if (!application) {
        return (
            <div className={page}>
                <Navbar />
                <div className={content}>
                    <p className="text-lg font-bold text-red-500">Not found.</p>
                    <Link to={backPath} className={backLink}>← Back</Link>
                </div>
            </div>
        )
    }

    const desc = application.descriptor
    const hasControlDevices = (desc.control_devices?.length ?? 0) > 0
    const grid = hasControlDevices
        ? "grid grid-cols-1 lg:grid-cols-2 gap-6"
        : "grid grid-cols-1 gap-6"

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                {/* HEADER */}
                <div className={header}>
                    <div className={titleBlock}>
                        <Link to={backPath} className={backLink}>← Back to {type === 'device' ? 'Devices' : 'Applications'}</Link>
                        <h1 className={heading}>{desc.name}</h1>
                        <StatusBadge status={application.status} />
                        {desc.description && (
                            <p className="text-sm text-gray-600 max-w-xl mt-1">{desc.description}</p>
                        )}
                    </div>

                    <div className={actions}>
                        <button
                            className={primaryBtn}
                            disabled={application.status !== 'free' || starting}
                            style={application.status !== 'free' ? { opacity: 0.4, cursor: 'not-allowed' } : {}}
                            onClick={handleStartSession}
                        >
                            {starting ? 'Starting…' : 'Start session now'}
                        </button>
                        <button
                            className={secondaryBtn}
                            onClick={() => user ? navigate(`/book/${type}/${id}`) : navigate('/login')}
                        >
                            Book a time slot
                        </button>
                        {startError && (
                            <p className="w-full text-sm font-medium text-red-600 mt-1">{startError}</p>
                        )}
                    </div>
                </div>

                {/* ── DESCRIPTOR CARDS ─────────────────────────── */}
                <div className={grid}>

                    {/* Main device descriptor */}
                    <div className={card}>
                        <p className={cardTitle}>Main device</p>
                        <JsonRenderer data={desc.main_device} />
                    </div>

                    {/* Control devices — only shown when the application has control boards */}
                    {hasControlDevices && (
                        <div className={card}>
                            <p className={cardTitle}>Control device{desc.control_devices.length > 1 ? 's' : ''}</p>
                            <JsonRenderer data={{ control_devices: desc.control_devices }} />
                        </div>
                    )}

                </div>

            </div>
        </div>
    )
}
