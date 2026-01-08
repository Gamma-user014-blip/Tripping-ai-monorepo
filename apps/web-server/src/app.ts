import express from 'express';
import dotenv from 'dotenv';
import { router } from './routes';

dotenv.config();

const app = express();
const port = process.env.PORT || 4000;

app.use(express.json());
app.use('/api', router);

app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'web-server-gateway' });
});

app.listen(port, () => {
    console.log(`Gateway listening at http://localhost:${port}`);
});
