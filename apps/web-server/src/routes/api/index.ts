import { Router } from "express";
import authRouter from "./auth";
import calendarRouter from "./calendar";
import chatRouter from "./chat";
import searchRouter from "./search";
import tripsRouter from "./trips";

const router: Router = Router();

router.use("/auth", authRouter);
router.use("/calendar", calendarRouter);
router.use(chatRouter);
router.use("/search", searchRouter);
router.use(tripsRouter);

export default router;
