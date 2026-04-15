import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {

  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const nav = "w-full bg-white border-b-2 border-black px-6 py-4 flex items-center justify-between font-body"

  const logo = [
    "text-2xl font-bold tracking-tight",
    "bg-accent px-3 py-1",
    "border-2 border-black rounded-none",
    "shadow-nb-sm",
    "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
    "transition-all duration-100"
  ].join(" ")

  const loginBtn = [
    "px-4 py-2",
    "border-2 border-black rounded-none",
    "font-medium",
    "hover:bg-black hover:text-white",
    "transition-colors duration-100"
  ].join(" ")

  const registerBtn = [
    "px-4 py-2",
    "bg-accent border-2 border-black rounded-none",
    "font-bold",
    "shadow-nb-sm",
    "hover:shadow-none hover:translate-x-[3px] hover:translate-y-[3px]",
    "transition-all duration-100"
  ].join(" ")

  const logoutBtn = [
    "px-4 py-2",
    "border-2 border-black rounded-none",
    "font-medium",
    "hover:bg-black hover:text-white",
    "transition-colors duration-100",
    "cursor-pointer"
  ].join(" ")

  const userName = "text-sm font-bold text-navy"

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  return (
    <nav className={nav}>
      <Link to="/" className={logo}>Remote32</Link>

      <div className="flex items-center gap-3">
        {user ? (
          <>
            <span className={userName}>{user.name}</span>
            <button className={logoutBtn} onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <Link to="/login" className={loginBtn}>Login</Link>
            <Link to="/register" className={registerBtn}>Register</Link>
          </>
        )}
      </div>
    </nav>
  )
}
