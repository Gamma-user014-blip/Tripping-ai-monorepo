import express from 'express';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const port = process.env.PORT || 4001;

app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'llm-chat-service' });
});

app.listen(port, () => {
    console.log(`LLM Chat Service listening at http://localhost:${port}`);
});
