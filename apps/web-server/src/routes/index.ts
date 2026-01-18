import { Router } from 'express';

export const router = Router();

router.get('/', (req, res) => {
    res.send('API Gateway Root');
});

// Placeholder for proxy routes
// router.use('/chat', chatProxy);
// router.use('/trip', tripProxy);
