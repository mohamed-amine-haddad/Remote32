import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import JsonRenderer from '../components/JsonRenderer'

// Mock data
const DEVICES = {
    1: {
        status: "free",
        descriptor: {
            name: "STM32-01",
            type: "STM32F4 Discovery",
            openocd_config_path: "board/stm32f4discovery.cfg",
            serial_port: "/dev/ttyUSB0",
            swd_interface: "stlink",
            camera: {
                enabled: true,
                stream_path: "/stream/device1",
                resolution: "1280x720",
            },
            capabilities: ["GPIO", "UART", "SPI", "I2C", "PWM", "ADC"],
            notes: "General-purpose board. Suitable for most beginner and intermediate labs.",
        }
    },
    2: {
        status: "occupied",
        descriptor: {
            name: "STM32-02",
            type: "STM32G0 Nucleo",
            openocd_config_path: "board/stm32g0nucleo.cfg",
            serial_port: "/dev/ttyUSB1",
            swd_interface: "stlink",
            camera: {
                enabled: true,
                stream_path: "/stream/device2",
                resolution: "640x480",
            },
            capabilities: ["GPIO", "UART", "ADC", "DAC", "Low-power modes"],
            notes: null,
        }
    },
}

export default function DeviceDetailPage() {

    // useParams reads the :id from the URL — e.g. /devices/1 gives { id: "1" }
    const { id } = useParams()
    const device = DEVICES[id]

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

    // 404 fallback
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

                    {/* Action buttons — disabled visually if not free */}
                    <div className={actions}>
                        <button
                            className={primaryBtn}
                            disabled={device.status !== 'free'}
                            style={device.status !== 'free' ? { opacity: 0.4, cursor: 'not-allowed' } : {}}
                        >
                            Start session now
                        </button>
                        <Link to={`/book/device/${id}`} className={secondaryBtn}>
                            Book a time slot
                        </Link>
                    </div>
                </div>

                {/* DESCRIPTOR CARD */}
                <div className={card}>
                    <p className={cardTitle}>Hardware descriptor</p>
                    {/* JsonRenderer takes the full descriptor object and renders it dynamically */}
                    <JsonRenderer data={device.descriptor} />
                </div>

            </div>
        </div>
    )
}