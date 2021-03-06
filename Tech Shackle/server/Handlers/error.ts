import { Request, Response, NextFunction } from 'express';
import { CustomError } from './custom-types';

const errorHandler = (
  error: CustomError,
  req: Request,
  res: Response,
  next: NextFunction
) =>
  res.status(error.status || 500).json({
    error: {
      message: error.message || 'Oops.. something went wrong!!',
    },
  });

export default errorHandler;
