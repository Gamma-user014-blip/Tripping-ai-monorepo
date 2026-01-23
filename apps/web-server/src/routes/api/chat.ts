import type { Request, Response } from "express";
import { Router } from "express";
import { getNextChatMessageCount } from "../../chat/chat-session-store";
import { startSearch } from "../../search/search-store";
import type { ChatRequest, ChatResponse } from "@monorepo/shared";
import { ChatResponseStatus } from "@monorepo/shared";
import {
  getSingleMissingQuestion,
  updateTripYaml,
  FillStatus,
} from "../../chat/essential-data-util";
import yaml from "js-yaml";

const router: Router = Router();

let tripYml = `
meta:
  schema: trip_intake
  timezone: Asia/Jerusalem

conversation:
  rawPrompt: ""
  history:
    lastUserPrompts: []
    summary: ""
  messages: []

trip:
  essentials:
    travelers:
      adults: null
      children: 0
      infants: 0
      childrenAges: []
      rooms: 1

    origin:
      kind: airport_or_city
      iata: null
      city: null
      countryCode: null

    destinations:
      - kind: airport_or_city_or_region
        iata: null
        city: null
        countryCode: null
        region: null

    dates:
      mode: fixed_or_flexible
      departureDate: null
      returnDate: null
      nights: null
      flex:
        plusMinusDays: 0
        departDOW: []
        returnDOW: []

    packageScope:
      includeFlight: true
      includeHotel: true
      includeTransfers: null
      includeCarRental: null
      includeActivities: null

    currency: USD

  preferences:
    budget:
      mode: total_or_perPerson_or_perNight
      amount: null
      currency: null
      hardCap: false

    hotel:
      starMin: null
      starMax: null
      board: null
      propertyTypes: []
      amenities:
        wifi: null
        pool: null
        gym: null
        spa: null
      locationPrefs:
        near: []
        areas: []
        avoid: []
        maxDistanceKm: null

  classification:
    summary:
      primaryArchetype: null
      secondaryArchetypes: []
      confidence: 0.0
      userConfirmNeeded: false

    labels:
      archetypes: []
      themes: []
      geoIntents: []
      activityIntents: []
      landmarkIntents: []

    derivedConstraints:
      geoConstraints:
        preferCoastal: null
        maxDistanceToCoastKm: null
        preferCityCenter: null
        maxDistanceToCenterKm: null
      activityConstraints:
        foodTourismPriority: null
        museumPriority: null
        hikingPriority: null
        nightlifePriority: null
      routingHints:
        suggestDestinationsAllowed: true
        mustIncludeLandmark: false
        mustBeInSpecificCity: false

    specialNotes: []

  extraction:
    status:
      state: collecting_or_ready_or_error
      readyForNextModule: false
    blockingMissing: []
`;

router.post("/chat", async (req: Request, res: Response): Promise<void> => {
  const body = req.body as Partial<ChatRequest>;
  const message = body.message;
  const sessionId = body.sessionId;

  // Checks for data

  if (!message || typeof message !== "string") {
    res.status(400).json({ error: "Message is required" });
    return;
  }

  if (!sessionId || typeof sessionId !== "string") {
    res.status(400).json({ error: "Session ID is required" });
    return;
  }

  // Start logic of processign the data given by the user

  console.log("Message: " + message);

  const updateTripYamlResponse = await updateTripYaml(message, tripYml);
  tripYml = updateTripYamlResponse.yaml;

  const getSingleMissingQuestionResponse = await getSingleMissingQuestion(
    updateTripYamlResponse.yaml,
  );

  let aiResponse: string;

  if (getSingleMissingQuestionResponse.status != FillStatus.ready) {
    aiResponse = getSingleMissingQuestionResponse.message!;
  } else {
    aiResponse = yaml.load(updateTripYamlResponse.yaml) as string;
  }

  const messageCount: number = getNextChatMessageCount(sessionId);

  const isComplete = messageCount === 2;
  let searchId: string | undefined;

  if (isComplete) {
    searchId = startSearch();
  }

  const response: ChatResponse = {
    message: !isComplete
      ? `${aiResponse} ${messageCount}`
      : "Generating your trip...",
    status: isComplete
      ? ChatResponseStatus.COMPLETE
      : ChatResponseStatus.INCOMPLETE,
    searchId,
  };
  res.json(response);
});

export default router;
