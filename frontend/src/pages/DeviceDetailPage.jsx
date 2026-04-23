import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import JsonRenderer from '../components/JsonRenderer'
import { useAuth } from '../contexts/AuthContext'
import { apiGetDevice } from '../api/devices'

export default function DeviceDetailPage() {

    const { id } = useParams()
    const navigate = useNavigate()
    const { user } = useAuth()
    const [device, setDevice] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        apiGetDevice(id)
            .then(setDevice)
            .catch(() => setDevice(null))
            .finally(() => setLoading(false))
    }, [id])

    function requireAuth(destination) {
        if (user) {
            navigate(destination)
        } else {
            navigate('/login')
        }
    }

    // Layout
    const page = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    // Header row
    const header = "flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-10"
    const titleBlock = "flex flex-col gap-2"
    const heading = "font-display text-5xl md:text-6xl text-navy"
    const backLink = "text-xs font-bold uppercase tracking-widest text-gray-400 hover:text-black underline underline-offset-2"

    // Action buttons
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

    // Descriptor card
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

    if (!device) {
        return (
            <div className={page}>
                <Navbar />
                <div className={content}>
                    <p className="text-lg font-bold text-red-500">Device not found.</p>
                    <Link to="/devices" className={backLink}>← Back to Devices</Link>
                </div>
            </div>
        )
    }

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                {/* HEADER */}
                <div className={header}>
                    <div className={titleBlock}>
                        <Link to="/devices" className={backLink}>← Back to Devices</Link>
                        <h1 className={heading}>{device.descriptor.name}</h1>
                        <StatusBadge status={device.status} />
                    </div>

                    {/* Action buttons — Start/Book require auth; Start also requires device to be free */}
                    <div className={actions}>
                        <button
                            className={primaryBtn}
                            disabled={device.status !== 'free'}
                            style={device.status !== 'free' ? { opacity: 0.4, cursor: 'not-allowed' } : {}}
                            onClick={() => requireAuth(`/session/device/${id}`)}
                        >
                            Start session now
                        </button>
                        <button
                            className={secondaryBtn}
                            onClick={() => requireAuth(`/book/device/${id}`)}
                        >
                            Book a time slot
                        </button>
                    </div>
                </div>

                {/* DESCRIPTOR CARD */}
                <div className={card}>
                    <p className={cardTitle}>Hardware descriptor</p>
                    <JsonRenderer data={device.descriptor} />
                </div>

            </div>
        </div>
    )
}
