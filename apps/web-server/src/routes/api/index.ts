import { Router } from "express";
import chatRouter from "./chat";
import searchRouter from "./search";
import tripsRouter from "./trips";

const router: Router = Router();

router.use(chatRouter);
router.use("/search", searchRouter);
router.use(tripsRouter);

export default router;
