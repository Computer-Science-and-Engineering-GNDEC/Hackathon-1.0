import express from 'express';

// const authHandler = require("./../Handlers/authHandler");
const router = express.Router();

import {
  /* forgotPassword */ signIn,
  signUp,
  forgotPassword,
} from '../Handlers/auth';
import { deleteDocument } from '../Handlers/delete';

// Router.post('/signin', signIn)
//   .post('/forgotPassword', forgotPassword)
//   .post('/signup', signUp)
//   .delete('/:id', deleteDocument);

router.post('/signup', signUp);

export default router;
