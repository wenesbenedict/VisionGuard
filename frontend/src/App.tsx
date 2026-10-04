import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Incidents from './pages/Incidents'
import Cameras from './pages/Cameras'
import Analyze from './pages/Analyze'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <nav className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex gap-6 items-center">
          <span className="font-bold text-sky-400">VISIONGUARD</span>
          <Link to="/" className="hover:text-sky-400">Dashboard</Link>
          <Link to="/incidents" className="hover:text-sky-400">Incidents</Link>
          <Link to="/cameras" className="hover:text-sky-400">Cameras</Link>
          <Link to="/analyze" className="hover:text-sky-400">Analyze</Link>
        </nav>
        <main className="p-6 max-w-6xl mx-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/cameras" element={<Cameras />} />
            <Route path="/analyze" element={<Analyze />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
