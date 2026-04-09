import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import clsx from 'clsx'

// Mock data
const APPLICATIONS = [
    {
        id: 1,
        name: "Motor Control Lab",
        status: "free",
        description: "Full closed-loop DC motor control application. Main STM32 runs a PID controller over PWM. Control board sends speed setpoint commands and direction signals over UART. Includes encoder feedback and current sensing.",
    },
    {
        id: 2,
        name: "Sensor Array",
        status: "reserved",
        description: "Multi-sensor data acquisition platform. Main device aggregates readings from temperature, pressure, and proximity sensors over I2C. Control board triggers sampling sequences and configures sensor modes via UART commands.",
    },
    {
        id: 3,
        name: "Communication Bus Demo",
        status: "occupied",
        description: "Demonstrates CAN bus communication between two STM32 nodes. The main device acts as a master node, while the control board simulates a slave ECU responding to standardized message frames.",
    },
]

export default function ApplicationsPage() {

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

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                <h1 className={heading}>Applications</h1>
                <p className={subheading}>
                    {APPLICATIONS.length} application{APPLICATIONS.length !== 1 ? 's' : ''} available — Select application for more details
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
                        {APPLICATIONS.map(app => (
                            <tr key={app.id} className={tr}>
                                <td className={td}>
                                    <Link to={`/applications/${app.id}`} className={nameLink}>
                                        {app.name}
                                    </Link>
                                </td>
                                <td className={td}>
                                    <StatusBadge status={app.status} />
                                </td>
                                <td className={td}>
                                    <p className={descText}>{app.description}</p>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* MOBILE CARDS */}
                <div className={cardList}>
                    {APPLICATIONS.map(app => (
                        <div key={app.id} className={card}>
                            <div className={cardHeader}>
                                <Link to={`/applications/${app.id}`} className={cardNameLink}>
                                    {app.name}
                                </Link>
                                <StatusBadge status={app.status} />
                            </div>
                            <p className={cardDesc}>{app.description}</p>
                        </div>
                    ))}
                </div>

            </div>
        </div>
    )
}