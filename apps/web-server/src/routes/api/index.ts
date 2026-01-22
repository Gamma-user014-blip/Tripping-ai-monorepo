import { Router } from 'express'
import chatRouter from './chat'

const router: Router = Router()

router.use(chatRouter)

export default router
