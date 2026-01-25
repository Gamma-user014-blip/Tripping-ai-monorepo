import dotenv from "dotenv";
import path from "path";

// Construct full absolute path to your .env file
const envPath = path.resolve(__dirname, "../../../../.env"); // adjust relative path as needed

dotenv.config({ path: path.join(process.cwd(), ".env") });

import { Router, Request, Response } from "express";
import { google } from "googleapis";
import { Credentials } from "google-auth-library";
import { saveUserTokensMemory } from "../../db/tokenStore"; // adjust pathimport { v4 as uuidv4 } from "uuid"; 

const router: Router = Router();

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.BASE_URL || 'http://localhost:3001'}/api/auth/callback`
);

console.log('OAuth Client ID:', process.env.GOOGLE_CLIENT_ID);

// Route to initiate Google OAuth
// Route to initiate Google OAuth
router.get("/google", (req: Request, res: Response) => {
  const { state } = req.query; // generated in frontend

  if (!state || typeof state !== "string") {
    return res.status(400).send("Missing state");
  }

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: "offline",
    scope: ["https://www.googleapis.com/auth/calendar.events"],
    redirect_uri: `${
      process.env.BASE_URL || "http://localhost:3001"
    }/api/auth/callback`,
    state, // use the frontend-generated state
  });

  console.log("[Auth] Redirecting to Google OAuth, state:", state);
  res.redirect(authUrl);
});




// Callback route
router.get("/callback", async (req: Request, res: Response) => {
  const { code, state } = req.query;
  if (!code || typeof code !== "string" || !state || typeof state !== "string") {
    return res.status(400).json({ error: "Authorization code or state missing" });
  }

  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);

const userId = state as string;
saveUserTokensMemory(userId, tokens as Credentials);
    console.log("[Auth] Saved user tokens for userId (state):", userId);

    const frontendOrigin =
      process.env.FRONTEND_ORIGIN || "http://localhost:3000";

    res.send(`
      <html>
        <body>
          <script>
            console.log("[OAuth popup] callback loaded, state='${userId}'");
            try {
              if (!window.opener) {
                console.error("[OAuth popup] window.opener is null");
              } else {
                console.log("[OAuth popup] sending postMessage to '${frontendOrigin}'");
                window.opener.postMessage(
                  { status: "success", state: "${userId}", close: true },
                  "${frontendOrigin}"
                );
              }
              window.close();
            } catch (e) {
              console.error("[OAuth popup] error sending postMessage / closing", e);
            }
          </script>
        </body>
      </html>
    `);
  } catch (error) {
    console.error("Error exchanging code for tokens:", error);
    return res.status(500).json({ error: "Failed to authenticate" });
  }
});





export default router;