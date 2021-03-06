import { Request, Response, NextFunction } from 'express';
import { CustomError } from './custom-types';

const errorHandler = (
  error: CustomError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  return res.status(error.status || 500).json({
    message: error.message || 'Oops.. something went wrong!!',
  });
};

export default errorHandler;
