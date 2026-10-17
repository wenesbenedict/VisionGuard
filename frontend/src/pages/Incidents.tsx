import { useEffect, useState } from 'react'
import { getIncidents, setIncidentStatus } from '../api'
import type { Incident } from '../types'

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [error, setError] = useState('')

  const refresh = () => getIncidents().then(setIncidents).catch(err => setError(err.message || 'Failed to load incidents'))
  useEffect(() => { refresh() }, [])

  const cycle = async (i: Incident) => {
    const next = i.status === 'OPEN' ? 'UNDER_REVIEW' : i.status === 'UNDER_REVIEW' ? 'RESOLVED' : 'OPEN'
    setError('')
    try {
      await setIncidentStatus(i.id, next)
      refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update incident')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Incidents</h1>
      {error && <p role="alert" className="text-red-400 mb-3">{error}</p>}
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400 border-b border-slate-700">
            <th className="py-2">ID</th><th>Type</th><th>Severity</th><th>Camera</th><th>Description</th><th>Status</th><th>Time</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map(i => (
            <tr key={i.id} className="border-b border-slate-800">
              <td className="py-2">{i.id}</td>
              <td>{i.type}</td>
              <td>{i.severity}</td>
              <td>{i.camera_id}</td>
              <td className="max-w-xs truncate">{i.description}</td>
              <td>
                <button onClick={() => cycle(i)} className="px-2 py-1 bg-slate-700 rounded">
                  {i.status}
                </button>
              </td>
              <td>{new Date(i.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {incidents.length === 0 && <p className="text-slate-400 mt-4">No incidents recorded.</p>}
    </div>
  )
}
