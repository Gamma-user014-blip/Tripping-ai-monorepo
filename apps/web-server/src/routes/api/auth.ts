import dotenv from "dotenv";
dotenv.config();
import { Router, Request, Response } from "express";
import { google } from "googleapis";
import { saveUserTokens } from "../../db/mongo-util";
import { v4 as uuidv4 } from "uuid"; 

const router: Router = Router();

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.BASE_URL || 'http://localhost:3001'}/api/auth/callback`
);

console.log('OAuth Client ID:', process.env.GOOGLE_CLIENT_ID);

// Route to initiate Google OAuth
router.get("/google", (req: Request, res: Response) => {

      if (!req.session!.id) {
    req.session!.id = uuidv4();
    console.log("[Auth] Assigned session ID:", req.session!.id);
  }
    console.log("CLIENT_ID:", process.env.GOOGLE_CLIENT_ID);

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: ["https://www.googleapis.com/auth/calendar.events"],
    redirect_uri: `${process.env.BASE_URL || 'http://localhost:3001'}/api/auth/callback`,
    state: req.session!.id, // now guaranteed to exist
  });
    console.log("[Auth] Redirecting to Google OAuth, state:", req.session!.id);

  res.redirect(authUrl);
});

// Callback route
router.get("/callback", async (req: Request, res: Response) => {
  const { code, state } = req.query;
  if (!code || typeof code !== "string") {
    return res.status(400).json({ error: "Authorization code missing" });
  }

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

    // Store tokens in DB using session ID as userId
    const userId = state as string || req.session?.id;
    if (userId) {
      await saveUserTokens(userId, tokens);
            console.log("[Auth] Saved user tokens for userId:", userId);

    }
    req.session!.id = userId;

    // Redirect back to client or success page
    res.redirect(`${process.env.CLIENT_URL || 'http://localhost:3000'}/trip?auth=success`);
  } catch (error) {
    console.error("Error exchanging code for tokens:", error);
    res.status(500).json({ error: "Failed to authenticate" });
  }
});

export default router;