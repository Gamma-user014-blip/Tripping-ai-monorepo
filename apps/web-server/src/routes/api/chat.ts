import type { Request, Response } from 'express'
import { Router } from 'express'
import { getNextChatMessageCount } from '../../chat/chat-session-store'
import type { ChatRequest, ChatResponse } from '@monorepo/shared'
import { ChatResponseStatus } from '@monorepo/shared'
import { generatePlans } from '../../chat/json-agent-util'
import { TripPlan } from '../../chat/json-agent-util'

const router: Router = Router()

router.post('/chat', async (req: Request, res: Response): Promise<void> => {
  const body = req.body as Partial<ChatRequest>
  const message = body.message
  const sessionId = body.sessionId

  // Checks for data

  if (!message || typeof message !== 'string') {
    res.status(400).json({ error: 'Message is required' })
    return
  }

  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'Session ID is required' })
    return
  }

  // Start logic of processign the data given by the user

  const messageCount: number = getNextChatMessageCount(sessionId)

  const aiResponse: string = "ok"

  const delayMs: number =
    messageCount === 1
      ? 2000
      : messageCount === 2
        ? 3000
        : Math.floor(Math.random() * 3000) + 1000

  setTimeout(() => {
    const response: ChatResponse = {
      message: aiResponse,
      status: ChatResponseStatus.INCOMPLETE,
      searchId: "",
    }
    res.json(response)
  }, delayMs)
})

export default router
