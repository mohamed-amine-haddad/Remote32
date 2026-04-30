import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import clsx from 'clsx'
import { apiListDevices } from '../api/devices'

export default function DevicesPage() {

    const [devices, setDevices] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        apiListDevices()
            .then(setDevices)
            .catch(() => setDevices([]))
            .finally(() => setLoading(false))
    }, [])

    const page = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    const heading = "font-display text-5xl md:text-6xl text-navy mb-2"
    const subheading = "text-sm text-gray-500 mb-8"

    const table = "w-full border-2 border-black hidden md:table"
    const thead = "bg-navy text-white"
    const th = "px-4 py-3 text-left text-xs font-bold uppercase tracking-widest"
    const tr = "border-t-2 border-black hover:bg-yellow-50 transition-colors duration-100"
    const td = "px-4 py-4 align-top"

    const nameLink = [
        "font-bold text-navy",
        "underline underline-offset-2",
        "hover:text-black",
    ].join(" ")

    const descText = "text-sm text-gray-600 line-clamp-10"

    const cardList = "flex flex-col gap-4 md:hidden"

    const card = [
        "border-2 border-black rounded-none",
        "shadow-nb-sm",
        "p-4",
    ].join(" ")

    const cardHeader = "flex items-start justify-between gap-4 mb-2"
    const cardNameLink = "font-bold text-navy underline underline-offset-2 hover:text-black text-base"
    const cardDesc = "text-sm text-gray-600 line-clamp-10"

    if (loading) return (
        <div className={page}>
            <Navbar />
            <div className={content}>
                <p className="text-sm text-gray-400 font-medium">Loading devices…</p>
            </div>
        </div>
    )

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                <h1 className={heading}>Devices</h1>
                <p className={subheading}>
                    {devices.length} device{devices.length !== 1 ? 's' : ''} available — Select a device for direct GDB access
                </p>

                {/* DESKTOP TABLE */}
                <table className={table}>
                    <thead className={thead}>
                        <tr>
                            <th className={th}>Name</th>
                            <th className={th}>Status</th>
                            <th className={clsx(th, "w-full")}>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices.map(device => (
                            <tr key={device.id} className={tr}>
                                <td className={td}>
                                    <Link to={`/devices/${device.id}`} className={nameLink}>
                                        {device.name}
                                    </Link>
                                </td>
                                <td className={td}>
                                    <StatusBadge status={device.status} />
                                </td>
                                <td className={td}>
                                    <p className={descText}>{device.description}</p>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* MOBILE CARDS */}
                <div className={cardList}>
                    {devices.map(device => (
                        <div key={device.id} className={card}>
                            <div className={cardHeader}>
                                <Link to={`/devices/${device.id}`} className={cardNameLink}>
                                    {device.name}
                                </Link>
                                <StatusBadge status={device.status} />
                            </div>
                            <p className={cardDesc}>{device.description}</p>
                        </div>
                    ))}
                </div>

            </div>
        </div>
    )
}
