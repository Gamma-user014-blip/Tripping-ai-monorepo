import { Trip } from "./trip";

export enum ChatResponseStatus {
  COMPLETE = 200,
  INCOMPLETE = 202,
  FOLLOWUP = 201,
  EDITING = 203,
  DUPLICATE_SEARCH = 204,
  ERROR = 500,
}

export enum SearchStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  ERROR = "error",
}

export interface ChatRequest {
  message: string;
  sessionId: string;
}

export interface ChatResponse {
  message: string;
  status: ChatResponseStatus;
  searchId?: string;
}

export interface SearchPollRequest {
  searchId: string;
}

export interface SearchPollResponse {
  status: SearchStatus;
  results?: Trip[];
  tripIds?: string[];
  error?: string;
}
