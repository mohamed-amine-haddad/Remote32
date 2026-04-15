import { useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function LoginPage() {

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [rememberMe, setRememberMe] = useState(false)

    const handleSubmit = () => {
        console.log('Login:', { email, password, rememberMe })
    }

    // Layout
    const page = "min-h-screen bg-white font-body flex flex-col"
    const main = "flex-1 flex items-center justify-center px-4 py-16"

    // Card
    const card = [
        "w-full max-w-md",
        "border-2 border-black rounded-none",
        "shadow-nb",
        "p-8",
    ].join(" ")

    const cardTitle = "font-display text-5xl text-navy mb-1"
    const cardSubtitle = "text-sm text-gray-500 mb-8"

    // Form
    const fieldGroup = "flex flex-col gap-1 mb-5"
    const label = "text-xs font-bold uppercase tracking-widest text-navy"

    const input = [
        "w-full px-4 py-3",
        "border-2 border-black rounded-none",
        "font-body text-sm",
        "bg-white",
        "placeholder:text-gray-400",
        "focus:outline-none focus-visible:outline-3 focus-visible:outline-accent focus-visible:outline-offset-0",
    ].join(" ")

    // Remember me
    const rememberRow = "flex items-center gap-3 mb-6 cursor-pointer select-none"

    // Checkbox
    const checkbox = [
        "w-5 h-5 shrink-0",
        "border-2 border-black rounded-none",
        "accent-accent",
        "cursor-pointer",
    ].join(" ")

    const rememberLabel = "text-sm font-medium text-gray-700 cursor-pointer"

    const submitBtn = [
        "w-full py-3 mt-2",
        "bg-navy border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-white",
        "shadow-nb",
        "hover:shadow-none hover:translate-x-1 hover:translate-y-1",
        "transition-all duration-100",
        "cursor-pointer",
    ].join(" ")

    const footer = "mt-6 text-center text-sm text-gray-500"
    const footerLink = "font-bold text-navy underline underline-offset-2 hover:text-black"

    return (
        <div className={page}>
            <Navbar />
            <main className={main}>
                <div className={card}>

                    <h1 className={cardTitle}>Welcome back</h1>
                    <p className={cardSubtitle}>Log in to access your sessions and reservations</p>

                    {/* Email */}
                    <div className={fieldGroup}>
                        <label className={label}>Email</label>
                        <input
                            className={input}
                            type="email"
                            placeholder="example@email.com"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                        />
                    </div>

                    {/* Password */}
                    <div className={fieldGroup}>
                        <label className={label}>Password</label>
                        <input
                            className={input}
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>

                    {/* Remember me */}
                    <label className={rememberRow}>
                        <input
                            className={checkbox}
                            type="checkbox"
                            checked={rememberMe}
                            onChange={e => setRememberMe(e.target.checked)}
                        />
                        <span className={rememberLabel}>Remember me for 30 days</span>
                    </label>

                    {/* Submit */}
                    <button className={submitBtn} onClick={handleSubmit}>
                        Log in
                    </button>

                    <p className={footer}>
                        Don't have an account?{' '}
                        <Link to="/register" className={footerLink}>Register</Link>
                    </p>

                </div>
            </main>
        </div>
    )
}