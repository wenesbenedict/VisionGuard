import { useEffect, useState } from 'react'
import { getOverview, getIncidentsOverTime } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function Analytics() {
  const [overview, setOverview] = useState<any>(null)
  const [overTime, setOverTime] = useState<any[]>([])

  useEffect(() => {
    getOverview().then(setOverview).catch(() => {})
    getIncidentsOverTime().then(setOverTime).catch(() => {})
  }, [])

  if (!overview) return <p className="text-slate-400">Loading…</p>

  const byType = Object.entries(overview.by_type).map(([type, count]) => ({ type, count }))
  const byCamera = Object.entries(overview.by_camera).map(([camera, count]) => ({ camera, count }))

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Stat label="Total" value={overview.total} />
        <Stat label="Today" value={overview.today} />
        <Stat label="Open" value={overview.by_status?.OPEN ?? 0} />
        <Stat label="High" value={overview.by_severity?.HIGH ?? 0} />
      </div>
      <h2 className="text-lg font-semibold mb-2">By Type</h2>
      <div className="h-56 bg-slate-800 rounded p-4 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={byType}>
            <XAxis dataKey="type" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#38bdf8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <h2 className="text-lg font-semibold mb-2">By Camera</h2>
      <div className="h-56 bg-slate-800 rounded p-4 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={byCamera}>
            <XAxis dataKey="camera" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#a78bfa" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <h2 className="text-lg font-semibold mb-2">Over Time (7d)</h2>
      <div className="h-56 bg-slate-800 rounded p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={overTime}>
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="#34d399" />
          </LineChart>
        </ResponsiveContainer>
      </div>
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
