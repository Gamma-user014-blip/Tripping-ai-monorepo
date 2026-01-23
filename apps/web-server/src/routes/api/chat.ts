import type { Request, Response } from "express";
import { Router } from "express";
import type { ChatRequest, ChatResponse } from "@monorepo/shared";
import { ChatResponseStatus } from "@monorepo/shared";
import yaml from "js-yaml";
import { isDeepStrictEqual } from "node:util";
import {
  getSingleMissingQuestion,
  updateTripYaml,
  FillStatus,
} from "../../chat/essential-data-util";
import {
  appendChatMessage,
  getOrCreateSession,
  setTripYaml,
  markSearchCompleted,
  DEFAULT_TRIP_YAML,
} from "../../session/session-store";
import { startSearch, startMockSearch } from "../../search/search-service";

const MOCK_TRIGGER = "/mock";

const router: Router = Router();

const normalizeForComparison = (input: unknown): unknown => {
  if (input instanceof Date) {
    // js-yaml may parse YYYY-MM-DD into Date objects; normalize to ISO date string.
    return input.toISOString().slice(0, 10);
  }

  if (Array.isArray(input)) {
    return input.map((v) => normalizeForComparison(v));
  }

  if (input && typeof input === "object") {
    const record = input as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(record)) {
      const value = record[key];
      out[key] = value === undefined ? null : normalizeForComparison(value);
    }
    return out;
  }

  return input;
};

const asRecord = (input: unknown): Record<string, unknown> => {
  return input && typeof input === "object" && !Array.isArray(input)
    ? (input as Record<string, unknown>)
    : {};
};

const asArray = (input: unknown): unknown[] => {
  return Array.isArray(input) ? input : [];
};

const getSearchSignature = (yamlText: string): unknown => {
  try {
    const parsed = yaml.load(yamlText) as unknown;
    if (!parsed || typeof parsed !== "object") {
      return null;
    }

    const root = asRecord(parsed);
    const tripObj = asRecord(root["trip"]);
    const essentials = asRecord(tripObj["essentials"]);
    const preferences = asRecord(tripObj["preferences"]);

    const travelers = asRecord(essentials["travelers"]);
    const origin = asRecord(essentials["origin"]);
    const dates = asRecord(essentials["dates"]);

    const dep = dates["departureDate"] ?? null;
    const ret = dates["returnDate"] ?? null;
    const nights = dates["nights"] ?? null;

    // If returnDate is present, nights is redundant and may be re-derived by the model.
    const canonicalNights = ret ? null : nights;

    const destinations = asArray(essentials["destinations"]).map((d) => {
      const dd = asRecord(d);
      return {
        iata: dd["iata"] ?? null,
        city: dd["city"] ?? null,
        countryCode: dd["countryCode"] ?? null,
        region: dd["region"] ?? null,
      };
    });

    // Only include fields that affect search generation.
    // Ignore conversation/meta/history and also ignore derived/noisy fields.
    return {
      trip: {
        essentials: {
          travelers: {
            adults: travelers["adults"] ?? null,
            children: travelers["children"] ?? null,
            infants: travelers["infants"] ?? null,
            childrenAges: travelers["childrenAges"] ?? null,
            rooms: travelers["rooms"] ?? null,
          },
          origin: {
            iata: origin["iata"] ?? null,
            city: origin["city"] ?? null,
            countryCode: origin["countryCode"] ?? null,
          },
          destinations,
          dates: {
            mode: dates["mode"] ?? null,
            departureDate: dep,
            returnDate: ret,
            nights: canonicalNights,
          },
          packageScope: essentials["packageScope"] ?? null,
          currency: essentials["currency"] ?? null,
        },
        preferences,
      },
    };
  } catch {
    return null;
  }
};

const areSearchParamsSame = (yaml1: string, yaml2: string): boolean => {
  const sig1 = getSearchSignature(yaml1);
  const sig2 = getSearchSignature(yaml2);
  if (sig1 === null || sig2 === null) {
    return false;
  }
  console.log(sig1);
  console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
  console.log(sig2);
  return isDeepStrictEqual(
    normalizeForComparison(sig1),
    normalizeForComparison(sig2),
  );
};

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

  const session = getOrCreateSession(sessionId, DEFAULT_TRIP_YAML);

  // Check for mock trigger
  if (message.trim().toLowerCase() === MOCK_TRIGGER) {
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);
    const aiResponse = "Loading mock trip data...";
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

    const searchId = startMockSearch();
    markSearchCompleted(sessionId, DEFAULT_TRIP_YAML, "mock");

    const response: ChatResponse = {
      message: aiResponse,
      status: ChatResponseStatus.COMPLETE,
      searchId,
    };
    res.json(response);
    return;
  }

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);

  const yamlResponse = await updateTripYaml(message, session.tripYaml);
  setTripYaml(sessionId, DEFAULT_TRIP_YAML, yamlResponse.yaml);

  const questionResponse = await getSingleMissingQuestion(yamlResponse.yaml);
  const isComplete = questionResponse.status === FillStatus.ready;

  // If search would be complete, check if it's a duplicate
  if (isComplete && session.lastSearchYaml) {
    if (areSearchParamsSame(yamlResponse.yaml, session.lastSearchYaml)) {
      const aiResponse =
        "It looks like you're searching for the same trip again. Try changing some details like dates, destination, or number of travelers.";
      appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

      const response: ChatResponse = {
        message: aiResponse,
        status: ChatResponseStatus.DUPLICATE_SEARCH,
      };
      res.json(response);
      return;
    }
  }

  const aiResponse = isComplete
    ? "Great! I have all the information I need. Generating your trip..."
    : questionResponse.message!;

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

  const searchId = isComplete ? startSearch(yamlResponse.yaml) : undefined;

  if (isComplete && searchId) {
    markSearchCompleted(sessionId, DEFAULT_TRIP_YAML, yamlResponse.yaml);
  }

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
