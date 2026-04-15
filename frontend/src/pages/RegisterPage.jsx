import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { useAuth } from '../contexts/AuthContext'

export default function RegisterPage() {

    const { register } = useAuth()
    const navigate = useNavigate()

    const [name, setName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirm, setConfirm] = useState('')
    const [error, setError] = useState('')
    const [submitting, setSubmitting] = useState(false)

    const handleSubmit = async () => {
        setError('')
        if (password !== confirm) {
            setError('Passwords do not match')
            return
        }
        setSubmitting(true)
        try {
            await register(name, email, password)
            // Registration succeeds → redirect to login to get the cookie
            navigate('/login')
        } catch (err) {
            setError(err.message)
        } finally {
            setSubmitting(false)
        }
    }

    // Layout
    const page = "min-h-screen bg-white font-body flex flex-col"
    const main = "flex-1 flex items-center justify-center px-4 py-16"

    // Card — the centered form container
    const card = [
        "w-full max-w-md",
        "border-2 border-black rounded-none",
        "shadow-nb",
        "p-8",
    ].join(" ")

    const cardTitle = "font-display text-5xl text-navy mb-1"
    const cardSubtitle = "text-sm text-gray-500 mb-8"

    // Form layout
    const fieldGroup = "flex flex-col gap-1 mb-5"
    const label = "text-xs font-bold uppercase tracking-widest text-navy"

    const input = [
        "w-full px-4 py-3",
        "border-2 border-black rounded-none",
        "font-body text-sm",
        "bg-white",
        "placeholder:text-gray-400",
        // Focus: remove default browser outline, add our own via the global :focus-visible in index.css
        "focus:outline-none focus-visible:outline-3 focus-visible:outline-accent focus-visible:outline-offset-0",
    ].join(" ")

    const submitBtn = [
        "w-full py-3 mt-2",
        "bg-accent border-2 border-black rounded-none",
        "font-bold text-sm uppercase tracking-widest text-navy",
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

                    <h1 className={cardTitle}>Create account</h1>
                    <p className={cardSubtitle}>Join Remote32 to access the lab</p>

                    {/* Name */}
                    <div className={fieldGroup}>
                        <label className={label}>Full name</label>
                        <input
                            className={input}
                            type="text"
                            placeholder="Name Surname"
                            value={name}
                            onChange={e => setName(e.target.value)}
                        />
                    </div>

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

                    {/* Confirm password */}
                    <div className={fieldGroup}>
                        <label className={label}>Confirm password</label>
                        <input
                            className={input}
                            type="password"
                            placeholder="••••••••"
                            value={confirm}
                            onChange={e => setConfirm(e.target.value)}
                        />
                    </div>

                    {/* Error */}
                    {error && (
                        <p className="mb-4 text-sm text-red-600 font-medium">{error}</p>
                    )}

                    {/* Submit */}
                    <button className={submitBtn} onClick={handleSubmit} disabled={submitting}>
                        {submitting ? 'Creating account…' : 'Create account'}
                    </button>

                    <p className={footer}>
                        Already have an account?{' '}
                        <Link to="/login" className={footerLink}>Log in</Link>
                    </p>

                </div>
            </main>
        </div>
    )
}