const jwt = require("jsonwebtoken");
const crypto = require("crypto");
const DB = require("./../models");

const signToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET, {
    expiresIn: process.env.JWT_EXPIRES_IN,
  });
};

const createSendToken = (user, statusCode, req, res) => {
  const token = signToken(user._id);
  res.cookie("jwt", token, {
    expires: new Date(
      Date.now() + process.env.JWT_COOKIE_EXPIRES_IN * 24 * 60 * 60 * 1000
    ),
    httpOnly: true,
    secure: req.secure || req.headers("x-forwarded-proto") === "https",
  });
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
    res.status(200).json({
      status: "success",
      data: {
        newUser,
      },
    });
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
