import { useEffect, useState } from 'react'
import { getCameras, getZones, createZone, deleteZone, type Zone } from '../api'
import type { Camera } from '../types'

export default function Zones() {
  const [zones, setZones] = useState<Zone[]>([])
  const [cameras, setCameras] = useState<Camera[]>([])
  const [cameraId, setCameraId] = useState<number>(0)
  const [name, setName] = useState('')
  const [coords, setCoords] = useState('[[100,100],[400,100],[400,400],[100,400]]')

  const refresh = () => getZones().then(setZones).catch(() => {})
  useEffect(() => {
    refresh()
    getCameras().then(cs => { setCameras(cs); if (cs.length) setCameraId(cs[0].id) })
  }, [])

  const add = async (e: React.FormEvent) => {
    e.preventDefault()
    let coordinates: number[][]
    try {
      coordinates = JSON.parse(coords)
    } catch {
      alert('Coordinates must be JSON like [[x,y],[x,y],[x,y]]')
      return
    }
    await createZone({ camera_id: cameraId, name, coordinates, zone_type: 'RESTRICTED' })
    setName('')
    refresh()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Safety Zones</h1>
      <form onSubmit={add} className="space-y-2 mb-6 max-w-md">
        <select className="bg-slate-800 rounded p-2 w-full" value={cameraId} onChange={e => setCameraId(Number(e.target.value))}>
          {cameras.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input className="bg-slate-800 rounded p-2 w-full" placeholder="Zone name" value={name} onChange={e => setName(e.target.value)} required />
        <textarea className="bg-slate-800 rounded p-2 w-full" rows={2} value={coords} onChange={e => setCoords(e.target.value)} />
        <button className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2">Add Zone</button>
      </form>
      <ul className="space-y-2">
        {zones.map(z => (
          <li key={z.id} className="bg-slate-800 rounded p-3 flex justify-between">
            <span>{z.name} — camera {z.camera_id} — {z.coordinates.length} points</span>
            <button className="text-red-400" onClick={async () => { await deleteZone(z.id); refresh() }}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
