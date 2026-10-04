import { useEffect, useState } from 'react'
import { getCameras, analyzeVideo } from '../api'
import type { Camera } from '../types'

export default function Analyze() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [cameraId, setCameraId] = useState<number>(0)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<string>('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getCameras().then(setCameras).then(() => {}).catch(() => {})
  }, [])

  useEffect(() => {
    if (cameras.length && !cameraId) setCameraId(cameras[0].id)
  }, [cameras, cameraId])

  const run = async () => {
    if (!file || !cameraId) return
    setBusy(true); setResult('')
    try {
      const r = await analyzeVideo(file, cameraId)
      setResult(JSON.stringify(r, null, 2))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Analyze Video</h1>
      <div className="space-y-3 max-w-md">
        <select className="bg-slate-800 rounded p-2 w-full" value={cameraId} onChange={e => setCameraId(Number(e.target.value))}>
          {cameras.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input type="file" accept="video/*" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={run} disabled={busy} className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2 disabled:opacity-50">
          {busy ? 'Analyzing…' : 'Analyze'}
        </button>
        {result && <pre className="bg-slate-800 rounded p-3 text-sm overflow-auto">{result}</pre>}
      </div>
    </div>
  )
}
