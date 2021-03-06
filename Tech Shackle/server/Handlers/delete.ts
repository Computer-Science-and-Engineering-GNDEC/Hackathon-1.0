import { Request, Response, NextFunction } from 'express';
const db = require('../models');

export async function deleteDocument(
  req: Request,
  res: Response,
  next: NextFunction
) {
  try {
    const id = req.params.id;
    console.log(req.params);
    
    console.log(`id: ${id}`);
    

    // console.log(`id: ${id}, target: ${target}`);

    if (!id)
      return next({
        status: 400,
        message: 'No ID Provided for deleting!',
      });

      db.User.findByIdAndDelete(id, (err: Error) => {
        if (err) return next(err);
        else {
          console.log('deleted successfully');

          return res.status(200).json({
            message: 'song deleted successfully!',
          });
        }
      })
  } catch (error) {
    console.log(error);
    return next(error);
  }
}
