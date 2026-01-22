import { TripRequest } from '@monorepo/shared';

const JSON_AGENT_URL = process.env.JSON_AGENT_URL || 'http://json_agent:8000';

export interface TripPlan {
    vibe: string;
    actions: Array<Array<string | number | null>>;
}

export interface TripPlansResponse {
    plans: TripPlan[];
}

export interface GeneratePlansRequest {
    trip_yml: string;
}

export interface GeneratedTripResponse {
    vibe: string;
    trip_request: TripRequest;
}

export interface GenerateTripRequest {
    vibe: string;
    actions: Array<Array<string | number | null>>;
}

export interface EditTripPlansRequest {
    plans: TripPlan[];
    user_text: string;
}

export interface EditTripPlansResponse {
    plans: TripPlan[];
    modified_indices: number[];
}

/**
 * Generates 3 distinct trip plans (vibes) based on a trip description.
 */
export async function generatePlans(tripYml: string): Promise<TripPlan[]> {
    const response = await fetch(`${JSON_AGENT_URL}/api/generate-plans`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ trip_yml: tripYml } as GeneratePlansRequest),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate plans: ${response.statusText} - ${errorText}`);
    }

    const data = (await response.json()) as TripPlansResponse;
    return data.plans;
}

/**
 * Builds a full TripRequest object from a vibe and a sequence of actions.
 */
export async function buildTripRequest(vibe: string, actions: Array<Array<string | number | null>>): Promise<GeneratedTripResponse> {
    const response = await fetch(`${JSON_AGENT_URL}/api/build-trip-request`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vibe, actions } as GenerateTripRequest),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to build trip request: ${response.statusText} - ${errorText}`);
    }

    const data = (await response.json()) as GeneratedTripResponse;
    return data;
}

/**
 * Edits existing trip plans based on natural language instructions.
 */
export async function editPlans(plans: TripPlan[], userText: string): Promise<EditTripPlansResponse> {
    const response = await fetch(`${JSON_AGENT_URL}/api/edit-plans`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ plans, user_text: userText } as EditTripPlansRequest),
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to edit plans: ${response.statusText} - ${errorText}`);
    }

    const data = (await response.json()) as EditTripPlansResponse;
    return data;
}
