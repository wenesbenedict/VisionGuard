import { useEffect, useState } from 'react'
import { getCameras, createCamera } from '../api'
import type { Camera } from '../types'

export default function Cameras() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [name, setName] = useState('')
  const [source, setSource] = useState('')
  const [location, setLocation] = useState('')

  const refresh = () => getCameras().then(setCameras).catch(() => {})
  useEffect(() => { refresh() }, [])

  const add = async (e: React.FormEvent) => {
    e.preventDefault()
    await createCamera({ name, source, location })
    setName(''); setSource(''); setLocation('')
    refresh()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Cameras</h1>
      <form onSubmit={add} className="flex flex-wrap gap-2 mb-6">
        <input className="bg-slate-800 rounded p-2" placeholder="Name" value={name} onChange={e => setName(e.target.value)} required />
        <input className="bg-slate-800 rounded p-2" placeholder="Source" value={source} onChange={e => setSource(e.target.value)} required />
        <input className="bg-slate-800 rounded p-2" placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
        <button className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2">Add</button>
      </form>
      <ul className="space-y-2">
        {cameras.map(c => (
          <li key={c.id} className="bg-slate-800 rounded p-3 flex justify-between">
            <span>{c.name} — {c.location}</span>
            <span className="text-sm text-slate-400">{c.status}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
