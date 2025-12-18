import express, { Express, Request, Response, NextFunction } from 'express'
import cors from 'cors'
import apiRouter from './routes/api'

const app: Express = express()
const PORT: number = Number(process.env.PORT) || 3001

app.use(cors())
app.use(express.json())

app.use((req: Request, res: Response, next: NextFunction): void => {
  console.log(`[${req.method}] ${req.path}`)
  next()
})

app.use('/api', apiRouter)

app.listen(PORT, (): void => {
  console.log(`🚀 Server running on http://localhost:${PORT}`)
})
