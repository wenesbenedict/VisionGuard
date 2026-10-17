import { useEffect, useState } from 'react'
import { getCameras, getIncidents, getToken } from '../api'
import type { Camera, Incident } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [live, setLive] = useState<any[]>([])
  const [error, setError] = useState('')
  const [wsState, setWsState] = useState(() => getToken() ? 'Connecting to live alerts…' : 'Sign in to receive live alerts.')

  useEffect(() => {
    getCameras().then(setCameras).catch(err => setError(err.message || 'Failed to load cameras'))
    getIncidents().then(setIncidents).catch(err => setError(err.message || 'Failed to load incidents'))
    const token = getToken()
    if (!token) return
    const ws = new WebSocket(
      `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/incidents`,
      ['visionguard', `vg-auth.${token}`],
    )
    ws.onopen = () => setWsState('Live alerts connected.')
    ws.onmessage = e => {
      try {
        const data = JSON.parse(e.data)
        setLive(prev => [data, ...prev].slice(0, 10))
      } catch {
        setError('Received an unreadable live alert.')
      }
    }
    ws.onerror = () => setWsState('Live alerts could not connect.')
    ws.onclose = () => setWsState('Live alerts disconnected.')
    return () => ws.close()
  }, [])

  const byType = Object.entries(
    incidents.reduce<Record<string, number>>((acc, i) => {
      acc[i.type] = (acc[i.type] ?? 0) + 1
      return acc
    }, {}),
  ).map(([type, count]) => ({ type, count }))

  const high = incidents.filter(i => i.severity === 'HIGH').length

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Safety Dashboard</h1>
      {error && <p role="alert" className="text-red-400 mb-3">{error}</p>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Stat label="Cameras" value={cameras.length} />
        <Stat label="Incidents" value={incidents.length} />
        <Stat label="High Severity" value={high} />
        <Stat label="Open" value={incidents.filter(i => i.status === 'OPEN').length} />
      </div>

      <h2 className="text-lg font-semibold mb-2">Incidents by Type</h2>
      <div className="h-64 bg-slate-800 rounded p-4 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={byType}>
            <XAxis dataKey="type" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#38bdf8" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h2 className="text-lg font-semibold mb-2">Live Alerts</h2>
      <p className="text-slate-400 text-sm mb-2" aria-live="polite">{wsState}</p>
      <ul className="space-y-2 mb-6">
        {live.map((item, index) => (
          <li key={`${item.id ?? 'alert'}-${index}`} className="bg-red-950/40 border border-red-800 rounded p-3">
            {item.type} — {item.description}
          </li>
        ))}
        {live.length === 0 && <li className="text-slate-400">No live events received yet.</li>}
      </ul>

      <h2 className="text-lg font-semibold mb-2">Recent Incidents</h2>
      <ul className="space-y-2">
        {incidents.slice(0, 8).map(i => (
          <li key={i.id} className="bg-slate-800 rounded p-3 flex justify-between">
            <span>{i.type} — {i.description}</span>
            <span className="text-sm text-slate-400">{new Date(i.timestamp).toLocaleString()}</span>
          </li>
        ))}
        {incidents.length === 0 && <li className="text-slate-400">No incidents yet.</li>}
      </ul>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-slate-800 rounded p-4">
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-slate-400 text-sm">{label}</div>
    </div>
  )
}
