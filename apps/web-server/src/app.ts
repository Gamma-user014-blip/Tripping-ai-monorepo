import express, {
  type Express,
  type NextFunction,
  type Request,
  type Response,
} from "express";
import cors from "cors";
import cookieSession from "cookie-session";
import apiRouter from "./routes/api";

const app: Express = express();
const PORT: number = Number(process.env.PORT) || 3001;

app.use(
  cors({
    origin: true,
    credentials: true,
  }),
);

app.use(express.json());

app.use(
  cookieSession({
    name: "session",
    keys: [process.env.SESSION_SECRET || "dev-secret-key-change-in-production"],
    maxAge: 24 * 60 * 60 * 1000,
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  }) as any,
);

app.use((req: Request, res: Response, next: NextFunction): void => {
  console.log(
    `[${req.method}] ${req.path}  ${req.body ? JSON.stringify(req.body) : ""}`,
  );
  next();
});

app.use("/api", apiRouter);

app.listen(PORT, (): void => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
