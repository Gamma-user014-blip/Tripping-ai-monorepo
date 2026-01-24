import type { Request, Response } from "express";
import { Router } from "express";
import type { ChatRequest, ChatResponse } from "@monorepo/shared";
import { ChatResponseStatus } from "@monorepo/shared";
import {
  getSingleMissingQuestion,
  updateTripYaml,
  FillStatus,
} from "../../chat/essential-data-util";
import { editPlans, TripPlan } from "../../chat/json-agent-util";
import {
  appendChatMessage,
  getOrCreateSession,
  setTripYaml,
  markSearchCompleted,
  DEFAULT_TRIP_YAML,
  setTripPlans,
  getTripPlans,
  getBuiltTrips,
  setBuiltTrips,
} from "../../session/session-store";
import { startSearch, startMockSearch } from "../../search/search-service";

const MOCK_TRIGGER = "/mock";


const router: Router = Router();

async function handleMockRequest(
  sessionId: string,
  message: string,
): Promise<ChatResponse> {
  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);
  const aiResponse = "Loading mock trip data...";
  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

  const searchId = startMockSearch();
  markSearchCompleted(sessionId, DEFAULT_TRIP_YAML, "mock");

  return {
    message: aiResponse,
    status: ChatResponseStatus.COMPLETE,
    searchId,
  };
}

async function handleEditMode(
  sessionId: string,
  message: string,
  existingPlans: TripPlan[],
  tripYaml: string,
): Promise<ChatResponse> {
  console.log(`Edit mode detected for session ${sessionId}`);
  let aiResponse =
    "Got it! I'm updating your trip plans based on your feedback...";
  let searchId: string | undefined;

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

  try {
    const editResult = await editPlans(existingPlans, message);
    console.log(
      `Edited ${editResult.modified_indices.length} plans:`,
      editResult.modified_indices,
    );

    if (editResult.modified_indices.length === 0) {
      aiResponse = "I'm sorry, but I don't have enough information to make a decision. Please try again.";
      appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);
      return {
        message: aiResponse,
        status: ChatResponseStatus.INCOMPLETE,
        searchId,
      };
    }

    setTripPlans(sessionId, DEFAULT_TRIP_YAML, editResult.plans);

    // Get previous built trips to use as base results
    const previousBuiltTrips = getBuiltTrips(sessionId, DEFAULT_TRIP_YAML) || [];

    searchId = startSearch(
      tripYaml,
      editResult.plans,
      editResult.modified_indices,
      undefined, // onPlansGenerated
      previousBuiltTrips, // baseResults
      (updatedTrips) => {
        // Save the updated trips when search completes
        setBuiltTrips(sessionId, DEFAULT_TRIP_YAML, updatedTrips);
      },
    );
    markSearchCompleted(sessionId, DEFAULT_TRIP_YAML, tripYaml);
  } catch (error) {
    console.error("Error editing plans:", error);
    aiResponse =
      "Sorry, I had trouble updating your plans. Please try rephrasing your request.";
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);
  }

  return {
    message: aiResponse,
    status: ChatResponseStatus.EDITING,
    searchId,
  };
}

async function handleYamlMode(
  sessionId: string,
  message: string,
  currentYaml: string,
): Promise<ChatResponse> {
  const yamlResponse = await updateTripYaml(message, currentYaml);
  setTripYaml(sessionId, DEFAULT_TRIP_YAML, yamlResponse.yaml);

  const questionResponse = await getSingleMissingQuestion(yamlResponse.yaml);
  const isComplete = questionResponse.status === FillStatus.ready;

  let aiResponse: string;
  let searchId: string | undefined;

  if (isComplete) {
    aiResponse =
      "Great! I have all the information I need. Generating your trip...";
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);

    searchId = startSearch(
      yamlResponse.yaml,
      undefined,
      [0, 1, 2],
      async (plans) => {
        console.log(
          `Storing ${plans.length} generated plans for session ${sessionId}`,
        );
        setTripPlans(sessionId, DEFAULT_TRIP_YAML, plans);
      },
      undefined, // baseResults
      (builtTrips) => {
        // Save built trips when search completes
        console.log(
          `Storing ${builtTrips.length} built trips for session ${sessionId}`,
        );
        setBuiltTrips(sessionId, DEFAULT_TRIP_YAML, builtTrips);
      },
    );

    if (searchId) {
      markSearchCompleted(sessionId, DEFAULT_TRIP_YAML, yamlResponse.yaml);
    }
  } else {
    aiResponse = questionResponse.message!;
    appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "assistant", aiResponse);
  }

  return {
    message: aiResponse,
    status: isComplete
      ? ChatResponseStatus.COMPLETE
      : ChatResponseStatus.INCOMPLETE,
    searchId,
  };
}

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
    const response = await handleMockRequest(sessionId, message);
    res.json(response);
    return;
  }

  appendChatMessage(sessionId, DEFAULT_TRIP_YAML, "user", message);

  const existingPlans = getTripPlans(sessionId, DEFAULT_TRIP_YAML);
  const isEditMode = existingPlans && existingPlans.length > 0;

  let response: ChatResponse;
  if (isEditMode) {
    response = await handleEditMode(
      sessionId,
      message,
      existingPlans!,
      session.tripYaml,
    );
  } else {
    response = await handleYamlMode(sessionId, message, session.tripYaml);
  }

  res.json(response);
});


export default router;
