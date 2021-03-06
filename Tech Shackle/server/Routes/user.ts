import express from 'express';
import { deleteDocument } from '../Handlers/delete';

const router = express.Router();

/* prefixed with `/api/v1/users/:id` */

router.delete('/', deleteDocument);

export default router;
