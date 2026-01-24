import { MongoClient, Db, Collection } from "mongodb";
import { TripPlansResponse } from "../chat/json-agent-util";

const MONGODB_URI =
  process.env.MONGODB_URI || "mongodb://localhost:27017/tripping_ai";
const DB_NAME = MONGODB_URI.split("/").pop()?.split("?")[0] || "tripping_ai";

let client: MongoClient | null = null;
let db: Db | null = null;

export interface TripDocument {
  sessionId: string;
  tripPlansResponse: TripPlansResponse;
  yaml: string;
  updatedAt: Date;
}

export interface UserTokens {
  userId: string; // Use session ID or user ID
  googleTokens: any; // Tokens from Google
  updatedAt: Date;
}

export async function getDb(): Promise<Db> {
  if (db) return db;

  if (!client) {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
  }
  db = client.db(DB_NAME);

  // Ensure index on sessionId for faster lookups
  await db
    .collection("trip_plans")
    .createIndex({ sessionId: 1 }, { unique: true });

  return db;
}

export async function saveTripPlans(
  sessionId: string,
  tripPlansResponse: TripPlansResponse,
  yaml: string,
): Promise<void> {
  const database = await getDb();
  const collection: Collection<TripDocument> =
    database.collection("trip_plans");

  await collection.updateOne(
    { sessionId },
    {
      $set: {
        tripPlansResponse,
        yaml,
        updatedAt: new Date(),
      },
    },
    { upsert: true },
  );
}

export async function getTripPlans(
  sessionId: string,
): Promise<TripDocument | null> {
  const database = await getDb();
  const collection: Collection<TripDocument> =
    database.collection("trip_plans");

  return await collection.findOne({ sessionId });
}

export async function saveUserTokens(
  userId: string,
  googleTokens: any,
): Promise<void> {
  const database = await getDb();
  const collection: Collection<UserTokens> =
    database.collection("user_tokens");

  await collection.updateOne(
    { userId },
    {
      $set: {
        googleTokens,
        updatedAt: new Date(),
      },
    },
    { upsert: true },
  );
}

export async function getUserTokens(
  userId: string,
): Promise<UserTokens | null> {
  const database = await getDb();
  const collection: Collection<UserTokens> =
    database.collection("user_tokens");

  return await collection.findOne({ userId });
}

export async function closeConnection(): Promise<void> {
  if (client) {
    await client.close();
    client = null;
    db = null;
  }
}
