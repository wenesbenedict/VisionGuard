import type { Camera, Incident } from './types'

const base = '/api'
export const AUTH_CHANGE_EVENT = 'visionguard:auth-change'
export const UNAUTHORIZED_EVENT = 'visionguard:unauthorized'

export function getToken() {
  return localStorage.getItem('vg_token') ?? ''
}

export function logout() {
  localStorage.removeItem('vg_token')
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
}

function authHeaders(): Record<string, string> {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function apiRequest(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  for (const [key, value] of Object.entries(authHeaders())) {
    if (!headers.has(key)) headers.set(key, value)
  }
  const response = await fetch(`${base}${path}`, { ...init, headers })
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('vg_token')
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT))
    }
    let message = `Request failed (${response.status})`
    try {
      const body = await response.clone().json()
      if (typeof body.detail === 'string') message = body.detail
    } catch {
      // Keep the status-based message for non-JSON responses.
    }
    throw new Error(message)
  }
  return response
}

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await apiRequest(path, init)
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export async function login(email: string, password: string) {
  const data = await apiJson<{ access_token: string; role: string }>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  localStorage.setItem('vg_token', data.access_token)
  window.dispatchEvent(new Event(AUTH_CHANGE_EVENT))
  return data
}

export function getHealth(): Promise<{
  status: string
  database: string
  ppe_model_weights_available: boolean
}> {
  return apiJson('/health')
}

export function getCameras(): Promise<Camera[]> {
  return apiJson('/cameras')
}

export function getIncidents(): Promise<Incident[]> {
  return apiJson('/incidents')
}

export function createCamera(data: Partial<Camera>): Promise<Camera> {
  return apiJson('/cameras', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function setIncidentStatus(id: number, status: string): Promise<Incident> {
  return apiJson(`/incidents/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
}

export async function analyzeVideo(file: File, cameraId: number) {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('camera_id', String(cameraId))
  return apiJson<{
    camera_id: number
    frames_processed: number
    persons_detected: number
    incidents_created: number
    incident_ids: number[]
    ppe_detection_active: boolean
  }>('/analyze/video', { method: 'POST', body: fd })
}

export interface Zone {
  id: number
  camera_id: number
  name: string
  zone_type: string
  coordinates: number[][]
  created_at: string
}

export function getZones(): Promise<Zone[]> {
  return apiJson('/zones')
}

export function createZone(data: Partial<Zone>): Promise<Zone> {
  return apiJson('/zones', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function deleteZone(id: number): Promise<void> {
  return apiJson(`/zones/${id}`, { method: 'DELETE' })
}

export function getOverview() {
  return apiJson<{
    total: number
    today: number
    by_type: Record<string, number>
    by_severity: Record<string, number>
    by_status: Record<string, number>
    by_camera: Record<string, number>
  }>('/analytics/overview')
}

export function getIncidentsOverTime(): Promise<{ date: string; count: number }[]> {
  return apiJson('/analytics/incidents')
}
