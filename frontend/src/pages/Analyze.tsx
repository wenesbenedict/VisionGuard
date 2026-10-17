import { useEffect, useState } from 'react'
import { getCameras, analyzeVideo, getHealth } from '../api'
import type { Camera } from '../types'

export default function Analyze() {
  const [cameras, setCameras] = useState<Camera[]>([])
  const [cameraId, setCameraId] = useState<number>(0)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<string>('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>('')
  const [ppeWeightsAvailable, setPpeWeightsAvailable] = useState<boolean | null>(null)
  const [ppeActiveForRun, setPpeActiveForRun] = useState<boolean | null>(null)

  useEffect(() => {
    getCameras().then(setCameras).catch(err => {
      console.error('Failed to load cameras:', err)
      setError('Failed to load cameras')
    })
  }, [])

  useEffect(() => {
    getHealth()
      .then(health => setPpeWeightsAvailable(health.ppe_model_weights_available))
      .catch(err => setError(err.message || 'Could not verify backend health'))
  }, [])

  const selectedCameraId = cameraId || cameras[0]?.id || 0

  const run = async () => {
    setError('')
    if (!file) {
      setError('Please select a video file')
      return
    }
    if (!selectedCameraId) {
      setError('Please select a camera')
      return
    }
    setBusy(true); setResult('')
    try {
      const r = await analyzeVideo(file, selectedCameraId)
      setResult(JSON.stringify(r, null, 2))
      setPpeActiveForRun(Boolean(r.ppe_detection_active))
    } catch (err: any) {
      setError(err.message || 'Analysis failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Analyze Video</h1>
      {ppeWeightsAvailable === false && <p role="status" className="text-amber-300 mb-3">PPE model weights are not available. Helmet and vest checks are inactive; this run cannot verify PPE compliance.</p>}
      {ppeActiveForRun === false && ppeWeightsAvailable !== false && <p role="status" className="text-amber-300 mb-3">The PPE model did not activate for this run. Helmet and vest checks were not performed.</p>}
      <div className="space-y-3 max-w-md">
        <select className="bg-slate-800 rounded p-2 w-full" value={selectedCameraId} onChange={e => setCameraId(Number(e.target.value))}>
          {cameras.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input type="file" accept="video/*" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={run} disabled={busy} className="bg-sky-600 hover:bg-sky-500 rounded px-4 py-2 disabled:opacity-50">
          {busy ? 'Analyzing...' : 'Analyze'}
        </button>
        {error && <p className="text-red-500">{error}</p>}
        {result && <pre className="bg-slate-800 rounded p-3 text-sm overflow-auto">{result}</pre>}
      </div>
    </div>
  )
}
