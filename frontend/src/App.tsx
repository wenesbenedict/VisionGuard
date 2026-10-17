import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import { AUTH_CHANGE_EVENT, getToken, logout, UNAUTHORIZED_EVENT } from './api'
import Dashboard from './pages/Dashboard'
import Incidents from './pages/Incidents'
import Cameras from './pages/Cameras'
import Analyze from './pages/Analyze'
import Zones from './pages/Zones'
import Analytics from './pages/Analytics'
import Login from './pages/Login'

function RequireAuth({ authenticated }: { authenticated: boolean }) {
  const location = useLocation()
  if (!authenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <Outlet />
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(() => Boolean(getToken()))

  useEffect(() => {
    const sync = () => setAuthenticated(Boolean(getToken()))
    window.addEventListener(AUTH_CHANGE_EVENT, sync)
    window.addEventListener(UNAUTHORIZED_EVENT, sync)
    return () => {
      window.removeEventListener(AUTH_CHANGE_EVENT, sync)
      window.removeEventListener(UNAUTHORIZED_EVENT, sync)
    }
  }, [])

  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <nav className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex gap-6 items-center">
          <span className="font-bold text-sky-400">VISIONGUARD</span>
          {authenticated && <>
            <Link to="/" className="hover:text-sky-400">Dashboard</Link>
            <Link to="/incidents" className="hover:text-sky-400">Incidents</Link>
            <Link to="/cameras" className="hover:text-sky-400">Cameras</Link>
            <Link to="/analyze" className="hover:text-sky-400">Analyze</Link>
            <Link to="/zones" className="hover:text-sky-400">Zones</Link>
            <Link to="/analytics" className="hover:text-sky-400">Analytics</Link>
          </>}
          {authenticated
            ? <button className="ml-auto hover:text-sky-400" onClick={logout}>Log out</button>
            : <Link to="/login" className="ml-auto hover:text-sky-400">Login</Link>}
        </nav>
        <main className="p-6 max-w-6xl mx-auto">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth authenticated={authenticated} />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/cameras" element={<Cameras />} />
              <Route path="/analyze" element={<Analyze />} />
              <Route path="/zones" element={<Zones />} />
              <Route path="/analytics" element={<Analytics />} />
            </Route>
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
