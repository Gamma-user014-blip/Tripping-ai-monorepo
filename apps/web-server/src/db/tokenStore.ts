// src/token-store.ts
import { Credentials } from "google-auth-library";

const inMemoryTokens = new Map<string, Credentials>();

export function saveUserTokensMemory(
  userId: string,
  tokens: Credentials,
): void {
  inMemoryTokens.set(userId, tokens);
}

export function getUserTokensMemory(
  userId: string,
): Credentials | null {
  return inMemoryTokens.get(userId) ?? null;
}

export function clearUserTokensMemory(userId: string): void {
  inMemoryTokens.delete(userId);
}
