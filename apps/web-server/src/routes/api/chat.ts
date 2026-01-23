import type { Request, Response } from "express";
import { Router } from "express";
import type { ChatRequest, ChatResponse } from "@monorepo/shared";
import { ChatResponseStatus } from "@monorepo/shared";
import {
  getSingleMissingQuestion,
  updateTripYaml,
  FillStatus,
} from "../../chat/essential-data-util";
import {
  appendChatMessage,
  getOrCreateSession,
  setTripYaml,
  DEFAULT_TRIP_YAML,
} from "../../session/session-store";
import { startSearch, startMockSearch } from "../../search/search-service";

const MOCK_TRIGGER = "/mock";

const router: Router = Router();

router.post("/chat", async (req: Request, res: Response): Promise<void> => {
  const { message, sessionId } = req.body as Partial<ChatRequest>;

  if (!message || typeof message !== "string") {
    res.status(400).json({ error: "Message is required" });
    return;
  }

  if (!sessionId || typeof sessionId !== "string") {
    res.status(400).json({ error: "Session ID is required" });
    return;
  }

  // Check for mock trigger
  if (message.trim().toLowerCase() === MOCK_TRIGGER) {
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);
    const aiResponse = "Loading mock trip data...";
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

    const searchId = startMockSearch();

    const response: ChatResponse = {
      message: aiResponse,
      status: ChatResponseStatus.COMPLETE,
      searchId,
    };
    res.json(response);
    return;
  }

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);

  const session = getOrCreateSession(sessionId, DEFAULT_TRIP_YAML);
  const yamlResponse = await updateTripYaml(message, session.tripYaml);
  setTripYaml(sessionId, DEFAULT_TRIP_YAML, yamlResponse.yaml);

  const questionResponse = await getSingleMissingQuestion(yamlResponse.yaml);
  const isComplete = questionResponse.status === FillStatus.ready;
  const aiResponse = isComplete
    ? "Generating your trip..."
    : questionResponse.message!;

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

  const searchId = isComplete ? startSearch(yamlResponse.yaml) : undefined;

  const response: ChatResponse = {
    message: aiResponse,
    status: isComplete
      ? ChatResponseStatus.COMPLETE
      : ChatResponseStatus.INCOMPLETE,
    searchId,
  };
  res.json(response);
});

export default router;
