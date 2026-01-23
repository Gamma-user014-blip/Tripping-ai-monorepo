import { Trip } from './trip'

export enum ChatResponseStatus {
  COMPLETE = 200,
  INCOMPLETE = 202,
  ERROR = 500,
}

export enum SearchStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  ERROR = 'error',
}

export interface ChatRequest {
  message: string
  sessionId: string
}

export interface ChatResponse {
  message: string
  status: ChatResponseStatus
  searchId?: string
}

export interface SearchPollRequest {
  searchId: string
}

export interface SearchPollResponse {
  status: SearchStatus
  results?: Trip[]
  error?: string
}
