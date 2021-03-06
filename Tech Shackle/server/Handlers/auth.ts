import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { validateEmail } from '../utils/validateEmail';
const db = require('../models');

export async function signIn(req: Request, res: Response, next: NextFunction) {
  try {
    // Finding a user
    const { email, password } = req.body;

    if (!email || !password)
      return next({
        status: 400,
        message: 'Incomplete credentials provided!',
      });

    if (!validateEmail(email))
      return next({
        status: 400,
        message: 'Email Provided is not valid!',
      });

    // if ((!email && !mobile) || !password)
    //   return next({
    //     status: 400,
    //     message: 'Incomplete details (mobile/email/password)',
    //   });

    const user = await db.User.findOne({ email });
    // else user = await db.User.findOne({ mobile });

    // If no user found
    if (!user)
      return next({
        status: 404,
        message: 'Given User does not exist in DB',
      });

    const { profileImageURL, role } = user;

    /* Comare Password
     * We added a utility `comparePassword` function to each User
     */
    const isMatch = await user.comparePassword(password);

    if (isMatch) {
      const token = jwt.sign(
        { email, profileImageURL, role },
        process.env.SECRET_KEY!,
        {
          expiresIn: '7d',
        }
      );

      return res.status(200).json({ email, token, profileImageURL, role });
    } else {
      return next({
        // 401 - Unauthorized
        status: 401,
        message: 'Invalid Credentials',
      });
    }
  } catch (error) {
    return next(error);
  }
}

export async function signUp(req: Request, res: Response, next: NextFunction) {
  try {
    // Create a user
    console.log(req.body);

    const { email, password } = req.body;

    if (!email || !password)
      return next({
        status: 400,
        message: 'Incomplete credentials provided!',
      });

    if (!validateEmail(email))
      return next({
        status: 400,
        message: 'Email Provided is not valid!',
      });

    const newUser = await db.User.create(req.body);
    const { id, name, profileImageURL, role } = newUser;

    // Create a token (signing a token)
    /* SECRET_KEY should not be null */
    const SECRET_KEY = process.env.SECRET_KEY!;
    const token = jwt.sign({ id, name, profileImageURL, role }, SECRET_KEY);

    return res.status(200).json({
      id,
      name,
      profileImageURL,
      role,
      token,
    });
  } catch (error) {
    // See what kind of error
    /* If validation fails */
    if (error.code === 11000) {
      error.message = 'Sorry, that email is already taken';
    }

    return next({
      status: 400,
      message: error.message,
    });
  }
}

export async function getAllUsers(
  req: Request,
  res: Response,
  next: NextFunction
) {
  try {
    const users = await db.User.find();
    console.log(users);

    return res.status(200).json(users);
  } catch (error) {
    return next(error);
  }
}

// exports.logout = (req: Request, res: Response, next: NextFunction) => {
//   res.cookie('jwt', 'loggedout', {
//     expires: new Date(Date.now() + 10 * 1000),
//     // http: true,
//   });
//   res.status(200).json({ status: 'success' });
// };

export const forgotPassword = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    //Get the user based on the posted mail
    const user = await db.User.findOne({ email: req.body.email });
    if (!user) {
      return next();
    }

    //Generate a random password reset token
    const resetToken = user.createPasswordResetToken();
    await user.save({ validateBeforeSave: false });
  } catch (error) {}
};
