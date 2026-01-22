import type { Request, Response } from 'express'
import { Router } from 'express'
import { getNextChatMessageCount } from '../../chat/chat-session-store'
import type { ChatRequest, ChatResponse } from '@shared/types'
import { ChatResponseStatus } from '@shared/types'

const router: Router = Router()

router.post('/chat', (req: Request, res: Response): void => {
  const body = req.body as Partial<ChatRequest>
  const message = body.message
  const sessionId = body.sessionId

  if (!message || typeof message !== 'string') {
    res.status(400).json({ error: 'Message is required' })
    return
  }

  if (!sessionId || typeof sessionId !== 'string') {
    res.status(400).json({ error: 'Session ID is required' })
    return
  }

  const messageCount: number = getNextChatMessageCount(sessionId)

  const aiResponse: string =
    messageCount === 1
      ? 'Hello'
      : messageCount === 2
        ? 'Yes, I agree'
        : 'Under construction'

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
