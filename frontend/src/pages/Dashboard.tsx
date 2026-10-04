import { useEffect, useState } from 'react'
import { getCameras, getIncidents } from '../api'
import type { Camera, Incident } from '../types'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [live, setLive] = useState<any[]>([])

  useEffect(() => {
    getCameras().then(setCameras).catch(() => {})
    getIncidents().then(setIncidents).catch(() => {})
    const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/incidents`)
    ws.onmessage = e => {
      try {
        const data = JSON.parse(e.data)
        setLive(prev => [data, ...prev].slice(0, 10))
      } catch {}
    }
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
      <ul className="space-y-2 mb-6">
        {live.map((l, i) => (
          <li key={i} className="bg-red-950/40 border border-red-800 rounded p-3">
            {l.type} — {l.description}
          </li>
        ))}
        {live.length === 0 && <li className="text-slate-400">Waiting for live events…</li>}
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
