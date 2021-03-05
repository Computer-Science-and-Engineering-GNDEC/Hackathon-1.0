// Load env variables
require('dotenv').config();

import express from 'express';
import cors from 'cors';
import { CustomError } from './Handlers/custom-types';
import errorHandler from './Handlers/error';

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

/* If no routes found */
app.use((req, res, next) => {
  const error: CustomError = new Error('Given routes does not exist');
  error.status = 404;
  next(error);
});

/* Middleware for using routes */

// app.use('/api/v1/users', authRouter);

/* use our error handler middleware */
app.use(errorHandler);

app.listen(PORT, () => console.log(`Server started on PORT ${PORT}`));
