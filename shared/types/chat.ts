export enum ChatResponseStatus {
  COMPLETE = 200,
  INCOMPLETE = 202,
  ERROR = 500,
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
