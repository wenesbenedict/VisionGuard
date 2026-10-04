import type { Camera, Incident } from './types'

const base = '/api'

export async function getCameras(): Promise<Camera[]> {
  const r = await fetch(`${base}/cameras`)
  return r.json()
}

export async function getIncidents(): Promise<Incident[]> {
  const r = await fetch(`${base}/incidents`)
  return r.json()
}

export async function createCamera(data: Partial<Camera>): Promise<Camera> {
  const r = await fetch(`${base}/cameras`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return r.json()
}

export async function setIncidentStatus(id: number, status: string): Promise<Incident> {
  const r = await fetch(`${base}/incidents/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  return r.json()
}

export async function analyzeVideo(file: File, cameraId: number) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('camera_id', String(cameraId))
  const r = await fetch(`${base}/analyze/video`, { method: 'POST', body: fd })
  return r.json()
}
