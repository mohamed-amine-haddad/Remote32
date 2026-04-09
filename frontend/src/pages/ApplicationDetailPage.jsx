import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import StatusBadge from '../components/StatusBadge'
import JsonRenderer from '../components/JsonRenderer'

// Mock data
const APPLICATIONS = {
    1: {
        status: "free",
        descriptor: {
            name: "Motor Control Lab",
            description: "Closed-loop DC motor control with PID. Control board manages speed and direction setpoints.",
            main_device: {
                device_id: "STM32-01",
                role: "PID controller — reads encoder, drives PWM output",
                openocd_config_path: "board/stm32f4discovery.cfg",
                camera: {
                    enabled: true,
                    stream_path: "/stream/app1",
                },
            },
            control_devices: [
                {
                    device_id: "STM32-03",
                    default_elf: "motor_control_v1.elf",
                    available_elfs: [
                        "motor_control_v1.elf",
                        "motor_control_v2_turbo.elf",
                        "motor_open_loop.elf",
                    ],
                    buttons: [
                        { label: "Start motor", uart_command: "CMD_START" },
                        { label: "Stop motor",  uart_command: "CMD_STOP"  },
                        { label: "Speed +10%",  uart_command: "CMD_SPD_UP" },
                        { label: "Speed -10%",  uart_command: "CMD_SPD_DN" },
                        { label: "Reverse",     uart_command: "CMD_REV" },
                    ],
                }
            ],
        }
    },
    2: {
        status: "reserved",
        descriptor: {
            name: "Sensor Array",
            description: "Multi-sensor data acquisition over I2C. Control board triggers sampling and configures sensor modes.",
            main_device: {
                device_id: "STM32-02",
                role: "I2C master — aggregates sensor readings",
                openocd_config_path: "board/stm32g0nucleo.cfg",
                camera: {
                    enabled: false,
                    stream_path: null,
                },
            },
            control_devices: [
                {
                    device_id: "STM32-04",
                    default_elf: "sensor_trigger_v1.elf",
                    available_elfs: [
                        "sensor_trigger_v1.elf",
                        "sensor_continuous.elf",
                    ],
                    buttons: [
                        { label: "Sample once",    uart_command: "CMD_SAMPLE" },
                        { label: "Continuous on",  uart_command: "CMD_CONT_ON" },
                        { label: "Continuous off", uart_command: "CMD_CONT_OFF" },
                    ],
                }
            ],
        }
    },
}

export default function ApplicationDetailPage() {

    const { id } = useParams()
    const application = APPLICATIONS[id]

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

    // Two-column grid on desktop for the two descriptor cards
    const grid = "grid grid-cols-1 lg:grid-cols-2 gap-6"

    const card = [
        "border-2 border-black rounded-none",
        "shadow-nb p-6 md:p-8",
    ].join(" ")

    const cardTitle = "text-xs font-bold uppercase tracking-widest text-gray-400 mb-6"

    if (!application) {
        return (
            <div className={page}>
                <Navbar />
                <div className={content}>
                    <p className="text-lg font-bold text-red-500">Application not found.</p>
                    <Link to="/applications" className={backLink}>← Back to Applications</Link>
                </div>
            </div>
        )
    }

    const desc = application.descriptor

    return (
        <div className={page}>
            <Navbar />
            <div className={content}>

                {/* HEADER */}
                <div className={header}>
                    <div className={titleBlock}>
                        <Link to="/applications" className={backLink}>← Back to Applications</Link>
                        <h1 className={heading}>{desc.name}</h1>
                        <StatusBadge status={application.status} />
                        {desc.description && (
                            <p className="text-sm text-gray-600 max-w-xl mt-1">{desc.description}</p>
                        )}
                    </div>

                    <div className={actions}>
                        <button
                            className={primaryBtn}
                            disabled={application.status !== 'free'}
                            style={application.status !== 'free' ? { opacity: 0.4, cursor: 'not-allowed' } : {}}
                        >
                            Start session now
                        </button>
                        <button className={secondaryBtn}>
                            Book a time slot
                        </button>
                    </div>
                </div>

                {/* ── DESCRIPTOR CARDS ─────────────────────────── */}
                {/* Application has two logical sections — split into two cards
                    so neither becomes overwhelming. Both use the same JsonRenderer. */}
                <div className={grid}>

                    {/* Main device descriptor */}
                    <div className={card}>
                        <p className={cardTitle}>Main device</p>
                        <JsonRenderer data={desc.main_device} />
                    </div>

                    {/* Control devices — can be multiple, hence the array */}
                    <div className={card}>
                        <p className={cardTitle}>Control device{desc.control_devices.length > 1 ? 's' : ''}</p>
                        <JsonRenderer data={{ control_devices: desc.control_devices }} />
                    </div>

                </div>

            </div>
        </div>
    )
}