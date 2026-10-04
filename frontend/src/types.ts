export interface Camera {
  id: number
  name: string
  source: string
  location: string
  status: string
  created_at: string
}

export interface Incident {
  id: number
  camera_id: number | null
  type: string
  severity: string
  confidence: number
  tracking_id: string | null
  description: string
  snapshot_url: string | null
  video_url: string | null
  ai_summary: string | null
  status: string
  timestamp: string
  created_at: string
}
