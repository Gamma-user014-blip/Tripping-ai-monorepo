import express, { Express, Request, Response, NextFunction } from "express";
import cors from "cors";
import cookieSession from "cookie-session";
import apiRouter from "./routes/api";

const app: Express = express();
const PORT: number = Number(process.env.PORT) || 3001;

app.use(
  cors({
    origin: process.env.CLIENT_URL || "http://localhost:3000",
    credentials: true,
  }),
);
app.use(express.json());

const sessionMiddleware = cookieSession({
  name: "session",
  keys: [process.env.SESSION_SECRET || "dev-secret-key-change-in-production"],
  maxAge: 24 * 60 * 60 * 1000, // 24 hours
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax",
});
app.use(sessionMiddleware as unknown as express.RequestHandler);

app.use((req: Request, res: Response, next: NextFunction): void => {
  console.log(`[${req.method}] ${req.path}`);
  next();
});

app.use("/api", apiRouter);

app.listen(PORT, (): void => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
