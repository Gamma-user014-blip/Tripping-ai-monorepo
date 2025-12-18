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
