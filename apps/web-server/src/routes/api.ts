import { Router } from 'express'
import type { Request, Response } from 'express'
import type { HealthResponse } from '@shared/types'

const router: Router = Router()

router.get('/health', (req: Request, res: Response<HealthResponse>): void => {
  console.log('Health check requested')
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
  })
})

export default router

// Temporary mock results endpoint for frontend development
router.get('/results', (req: Request, res: Response): void => {
  // Add 2-second delay to simulate loading
  setTimeout(() => {
    const results = [
    {
      id: '1',
      tripId: 'trip-uk-highlands-loop-2026',
      origin: { city: 'London', country: 'UK', airportCode: 'LHR', latitude: 51.47, longitude: -0.4543 },
      destination: { city: 'Batata', country: 'UK', airportCode: 'EDI', latitude: 55.9533, longitude: -3.1883 },
      startDate: '2026-07-12',
      endDate: '2026-07-20',
      price: { currency: 'USD', amount: 4250 },
      hotels: [],
      highlights: [],
      outboundFlight: null,
      returnFlight: null,
      mapCenter: { lat: 54.6, lng: -2.8 },
      mapZoom: 6,
      waypoints: [],
    },
  ]

    res.json(results)
  }, 2000)
})
