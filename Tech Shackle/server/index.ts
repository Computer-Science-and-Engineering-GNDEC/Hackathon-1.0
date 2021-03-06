// Load env variables
require('dotenv').config();
const cookieParser = require('cookie-parser');
import express from 'express';
import cors from 'cors';
import { CustomError } from './Handlers/custom-types';
import userRoutes from './Routes/user';
const bodyParser = require('body-parser');
import errorHandler from './Handlers/error';
const authRouter = require('./Routes/authRoutes.js');

const app = express();


app.use(cors());
app.use(express.json());
app.use(cookieParser());
/* Middleware for using routes */

app.use('/api/v1/users', authRouter);
// app.use('/api/v1/users/:id', userRoutes);

const PORT = process.env.PORT || 5000;

/* If no routes found */
app.use((req, res, next) => {
  const error: CustomError = new Error('Given routes does not exist');
  error.status = 404;
  next(error);
});

/* use our error handler middleware */
app.use(errorHandler);

app.listen(PORT, () => console.log(`Server started on PORT ${PORT}`));
