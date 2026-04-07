import { Link, useLocation } from 'react-router-dom'


export default function Navbar() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const nav = "w-full bg-white border-b-2 border-black px-6 py-4 flex items-center justify-between font-body"

  const logo = "text-2xl font-bold tracking-tight bg-accent px-3 py-1 border-2 border-black shadow-[3px_3px_0px_black] hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-100"

  const authRow = "flex items-center gap-3"

  const loginBtn = "px-4 py-2 border-2 border-black font-medium hover:bg-black hover:text-white transition-colors duration-100"

  const registerBtn = "px-4 py-2 bg-accent border-2 border-black font-bold shadow-[3px_3px_0px_black] hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px] transition-all duration-100"

  return (
    <nav className={nav}>
      <Link to="/" className={logo}>Remote32</Link>

      <div className={authRow}>
        <Link to="/login" className={loginBtn}>Login</Link>
        <Link to="/register" className={registerBtn}>Register</Link>
      </div>
    </nav>
  )
}