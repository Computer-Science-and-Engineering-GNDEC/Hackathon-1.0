const jwt = require("jsonwebtoken");
const crypto = require("crypto");
const DB = require("./../models");
const { create } = require("domain");
const User = require("./../models/user");

const signToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN,
  });
};

const createSendToken = (user, statusCode, res) => {
  const token = signToken(user._id);
  const cookieOptions = {
    expires: new Date(
      Date.now() + process.env.JWT_COOKIE_EXPIRES_IN * 24 * 60 * 60 * 1000
    ),
    httpOnly: true,
  };
  if (process.env.NODE_ENV === "production") cookieOptions.secure = true;

  res.cookie("jwt", token, cookieOptions);

  // Remove password from output
  user.password = undefined;

  res.status(statusCode).json({
    status: "success",
    token,
    data: {
      user,
    },
  });
};

exports.signup = async (req, res, next) => {
  try {
    const newUser = await DB.User.create(req.body);
    createSendToken(newUser, 201, res);
  } catch (error) {
    console.error(error);
    // See what kind of error
    /* If validation fails */
    if (error.code === 11000) {
      error.message = "Sorry, that email is already taken";
    }

    return next({
      status: 400,
      message: error.message,
    });
  }
};

exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;
    const user = await DB.User.findOne({ email }).select("+password");

    //Check if email and apssword are submitted by the client
    if (!email || !password) {
      return next();
    }
    //Check if user exists and the password is correct
    if (!user || !(await user.comparePassword(password, user.password))) {
      return next();
    }
    //Check if user is verified or not

    //Return a web token to the client
    createSendToken(user, 200, res);
  } catch (error) {
    console.log(error);
  }
};

exports.forgotPassword = async (req, res, next) => {
  try {
    //Get the user based on the posted mail
    const user = await DB.User.findOne({ email: req.body.email });
    if (!user) {
      return next();
    }

    //Generate a random password reset token
    const resetToken = user.createPasswordResetToken();
    await user.save({ validateBeforeSave: false });
  } catch (error) {}
};

exports.logout = (req, res) => {
  res.cookie("jwt", "loggedout", {
    expires: new Date(Date.now() + 10 * 1000),
    http: true,
  });
  res.status(200).json({ status: "success" });
};
