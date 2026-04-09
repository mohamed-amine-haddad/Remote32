import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function HomePage() {

  const page = "min-h-screen bg-white font-body"

  const hero = "px-6 md:px-16 lg:px-32 py-20 md:py-32 border-b-2 border-black"

  const heroTitle = "font-display text-6xl md:text-8xl leading-none mb-6 text-navy"

  const heroSubtitle = "text-lg text-gray-700 mb-10 leading-relaxed max-w-xl"

  const ctaRow = "flex flex-wrap gap-4"

  const primaryBtn = [
    "px-6 py-3",
    "bg-accent border-2 border-black rounded-none",
    "font-bold",
    "shadow-nb",
    "hover:shadow-none hover:translate-x-1 hover:translate-y-1",
    "transition-all duration-100"
  ].join(" ")

  const secondaryBtn = [
    "px-6 py-3",
    "bg-white border-2 border-black rounded-none",
    "font-bold",
    "shadow-nb",
    "hover:shadow-none hover:translate-x-1 hover:translate-y-1",
    "transition-all duration-100"
  ].join(" ")

  const howSection = "px-6 md:px-16 lg:px-32 py-20"

  const howTitle = "font-display text-4xl md:text-5xl mb-12 text-navy"

  const howGrid = "grid grid-cols-1 md:grid-cols-3 gap-6"

  return (
    <div className={page}>
      <Navbar />

      <section className={hero}>
        <h1 className={heroTitle}>Remote STM32 Lab</h1>
        <p className={heroSubtitle}>
          Flash, debug and control real STM32 microcontrollers
          directly from your browser — no hardware required on your end.
        </p>
        <div className={ctaRow}>
          <Link to="/devices" className={primaryBtn}>Browse Devices</Link>
          <Link to="/applications" className={secondaryBtn}>Browse Applications</Link>
        </div>
      </section>

      <section className={howSection}>
        <h2 className={howTitle}>How It Works</h2>
        <div className={howGrid}>
          <StepCard number="01" title="Pick a Device"
            description="Browse available STM32 boards or full lab applications. Book a slot or start immediately if it's free." />
          <StepCard number="02" title="Connect Your IDE"
            description="Enter the GDB server IP and port in STM32CubeIDE. Flash and debug exactly as if the board were on your desk." />
          <StepCard number="03" title="Watch Live"
            description="A live camera feed shows your board in real time. Send commands, switch firmware, and see the results instantly." />
        </div>
      </section>
    </div>
  )
}

function StepCard({ number, title, description }) {

  const card = "group border-2 border-black rounded-none p-6 shadow-nb flex flex-col gap-3 transition-transform duration-300 hover:scale-110"
  const num = "font-display text-5xl text-accent text-stroke transition-transform duration-300 group-hover:scale-110"
  const cardTitle = "font-bold text-lg text-navy transition-transform duration-300 group-hover:scale-110"
  const cardDesc = "text-gray-600 text-sm leading-relaxed transition-transform duration-300 group-hover:scale-110"

  return (
    <div className={card}>
      <span className={num}>{number}</span>
      <h3 className={cardTitle}>{title}</h3>
      <p className={cardDesc}>{description}</p>
    </div>
  )
}