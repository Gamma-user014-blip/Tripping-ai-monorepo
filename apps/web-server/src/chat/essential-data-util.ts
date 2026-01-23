const LLM_CHAT_ESSENTIALS_URL =
  process.env.LLM_CHAT_ESSENTIALS_URL || "http://llm_chat_essentials:8000";

export enum FillStatus {
  ready = "ready",
  needs_more_info = "needs_more_info",
  error = "error",
}

export interface UpdateTripRequest {
  raw_user_message: string;
  current_yaml_state: string;
}

export interface FillResponse {
  yaml: string;
  status: FillStatus;
  message?: string;
}

/**
 * Updates the trip YAML state based on a raw user message.
 */
export async function updateTripYaml(
  rawUserMessage: string,
  currentYamlState: string,
): Promise<FillResponse> {
  const response = await fetch(
    `${LLM_CHAT_ESSENTIALS_URL}/api/update_trip_yaml`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        raw_user_message: rawUserMessage,
        current_yaml_state: currentYamlState,
      } as UpdateTripRequest),
    },
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Failed to update trip YAML: ${response.statusText} - ${errorText}`,
    );
  }

  const data = (await response.json()) as FillResponse;
  return data;
}

/**
 * Gets a single missing question based on the current trip YAML state.
 */
export async function getSingleMissingQuestion(
  currentYamlState: string,
): Promise<FillResponse> {
  const response = await fetch(
    `${LLM_CHAT_ESSENTIALS_URL}/api/get_single_missing_question`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        raw_user_message: "", // Not used by the endpoint based on main.py but required by model
        current_yaml_state: currentYamlState,
      } as UpdateTripRequest),
    },
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Failed to get missing question: ${response.statusText} - ${errorText}`,
    );
  }

  const data = (await response.json()) as FillResponse;
  return data;
}
