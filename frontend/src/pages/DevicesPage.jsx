import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import clsx from 'clsx'

// Mock data
const DEVICES = [
    {
        id: 1,
        name: "STM32-01",
        status: "free",
        description: "STM32F4 Discovery board. General-purpose device suitable for GPIO, timers, UART, SPI and I2C experiments. Connected via SWD.",
    },
    {
        id: 2,
        name: "STM32-02",
        status: "occupied",
        description: "STM32G0 Nucleo board. Ideal for low-power experiments and ADC/DAC signal processing labs. Full debug access via SWD.",
    },
    {
        id: 3,
        name: "STM32-03",
        status: "reserved",
        description: "STM32H7 evaluation board. High-performance board with FPU support. Used for DSP and real-time control labs requiring floating-point operations.",
    },
    {
        id: 4,
        name: "STM32-04",
        status: "free",
        description: "STM32L4 Nucleo board configured for ultra-low-power mode experiments. Suitable for battery-powered system prototyping.",
    },
]

export default function DevicesPage() {

    const page = "min-h-screen bg-white font-body flex flex-col"
    const content = "flex-1 px-6 md:px-16 lg:px-32 py-12"

    const heading = "font-display text-5xl md:text-6xl text-navy mb-2"
    const subheading = "text-sm text-gray-500 mb-8"

    // Desktop table — hidden on mobile
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

    // Description text — line-clamp-2 limits to 2 lines with ellipsis
    // This keeps all rows the same height regardless of description length
    const descText = "text-sm text-gray-600 line-clamp-10"

    // Mobile cards — visible only on mobile, hidden on md+
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

                <h1 className={heading}>Devices</h1>
                <p className={subheading}>
                    {DEVICES.length} device{DEVICES.length !== 1 ? 's' : ''} available — Select device for more details
                </p>

                {/* DESKTOP TABLE */}
                <table className={table}>
                    <thead className={thead}>
                        <tr>
                            <th className={th}>Name</th>
                            <th className={th}>Status</th>
                            {/* Description column takes all remaining space */}
                            <th className={clsx(th, "w-full")}>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {DEVICES.map(device => (
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
                    {DEVICES.map(device => (
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
