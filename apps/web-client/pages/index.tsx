import { useEffect, useState } from 'react'
import { apiClient } from '../lib/api-client'
import type { HealthResponse } from '@shared/types'

export default function Home(): JSX.Element {
  const [health, setHealth] = useState<string>('checking...')

  useEffect(() => {
    apiClient.get<HealthResponse>('/api/health')
      .then((data) => setHealth(data.status))
      .catch(() => setHealth('disconnected'))
  }, [])

  return (
    <div>
      <h1>Trip Planner</h1>
      <p>Server Status: <strong>{health}</strong></p>
    </div>
  )
}
