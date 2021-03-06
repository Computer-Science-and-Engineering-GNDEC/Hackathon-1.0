require("dotenv").config();
const express = require("express");
const router = express.Router();
const { check, validationResult } = require("express-validator");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const crypto = require("crypto");
const nodemailer = require("nodemailer");
const ejs = require("ejs");
const path = require("path");
const auth = require("../../middleware/auth");

const User = require("../../models/User");
const { route } = require("./project");

// @route    GET api/auth
// @desc     Get User
// @access   Private
router.get("/", auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select("-password");
    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send("Server error");
  }
});

// @route    POST api/auth
// @desc     Authenticate user and get token
// @access   Public
router.post(
  "/",
  [
    check("zoho_mail", "Please enter a zoho mail").not().isEmpty(),
    check("password", "Password is required").exists(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { zoho_mail, password } = req.body;

    try {
      let user = await User.findOne({ zoho_mail });

      if (!user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "Invalid Credentials" }] });
      }

      const isMatch = await bcrypt.compare(password, user.password);

      if (!isMatch) {
        return res
          .status(400)
          .json({ errors: [{ msg: "Invalid Credentials" }] });
      }

      const payload = {
        user: {
          id: user.id,
        },
      };

      jwt.sign(
        payload,
        process.env.JWT_SECRET,
        { expiresIn: "3d" },
        (err, token) => {
          if (err) throw err;
          res.json({ token });
        }
      );
    } catch (err) {
      console.log(err.message);
      res.status(500).send("Server error");
    }
  }
);

// @route    POST api/auth/forgot-password
// @desc     Generate token for forgot password
// @access   Public
router.post(
  "/forgot-password",
  [check("zoho_mail", "Please input a valid zoho mail").isEmail()],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }
    try {
      const zoho_mail = req.body.zoho_mail;

      let user = await User.findOne({ zoho_mail });

      if (!user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "User does not exist!" }] });
      }

      let token = crypto.randomBytes(20).toString("hex");
      user.resetPasswordToken = token;
      user.resetPasswordExpires = Date.now() + 3600000; //expires in an hour

      // let resetUrl = "http://" + req.headers.host + "/reset/" + token;
      let resetUrl = "http://localhost:3000/reset/" + token;

      await user.save();

      // let testAccount = await nodemailer.createTestAccount(); //Needs to be removed
      const smtptrans = nodemailer.createTransport({
        service: "gmail",
        auth: {
          user: process.env.EMAIL,
          pass: process.env.PASSWORD,
        },
      });

      smtptrans.verify((error, success) => {
        if (error) {
          console.log(error);
          return res.status(500).send("Server Error");
        }
      });

      const html = await ejs.renderFile(
        path.join(__dirname, "..", "..", "views", "forgot.ejs"),
        {
          resetUrl: resetUrl,
        }
      );

      const mailOpts = {
        from: "lscgdashboard@gmail.com",
        to: zoho_mail,
        subject: "Reset Password",
        html: html,
      };

      smtptrans.sendMail(mailOpts, (err) => {
        if (err) {
          console.log(err);
          return res.send(err);
        }
        res.status(200).json({ message: "Please check your mail" });
      });
    } catch (err) {
      console.log(err.message);
      res.status(500).send("Server error");
    }
  }
);

// @route    GET /api/auth/reset/:token
// @desc     Render reset password page
// @access   Public
router.get("/reset/:token", async (req, res) => {
  try {
    let user = await User.findOne({
      resetPasswordToken: req.params.token,
      resetPasswordExpires: { $gt: Date.now() },
    });

    if (!user) {
      return res.status(400).json({
        errors: [
          { msg: "Password reset token is invalid or has been expired" },
        ],
      });
    }

    res.status(200).json({ message: "Success" });
  } catch (err) {
    console.log(err.message);
    res.status(500).send("Server error");
  }
});

// @route    POST /api/auth/reset/:token
// @desc     Update Password
// @access   Public
router.post("/reset/:token", async (req, res) => {
  try {
    let user = await User.findOne({
      resetPasswordToken: req.params.token,
      resetPasswordExpires: { $gt: Date.now() },
    });

    if (!user) {
      return res.status(400).json({
        errors: [
          { msg: "Password reset token is invalid or has been expired" },
        ],
      });
    }

    let password = req.body.password;
    user.password = password;
    user.resetPasswordToken = undefined;
    user.resetPasswordExpires = undefined;

    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(password, salt);

    await user.save();

    const smtptrans = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.EMAIL,
        pass: process.env.PASSWORD,
      },
    });

    smtptrans.verify((error, success) => {
      if (error) {
        console.log(error);
        return res.status(500).send("Server Error");
      }
    });

    const html = await ejs.renderFile(
      path.join(__dirname, "..", "..", "views", "confirm.ejs")
    );

    const mailOpts = {
      from: "lscgdashboard@gmail.com",
      to: user.zoho_mail,
      subject: "Your Password has been changed",
      html: html,
    };

    smtptrans.sendMail(mailOpts, (err) => {
      if (err) {
        console.log(err);
        return res.status(500).send("Server error");
      }
    });

    res.status(200).json({ message: "Your Password has been changed" });
  } catch (err) {
    console.log(err.message);
    res.status(500).send("Server error");
  }
});

// @route    GET /api/auth/user/:id
// @desc     GET user by id
// @access   Private
router.get("/user/:id", auth, async (req, res) => {
  const id = req.params.id;
  try {
    const user = await User.findById(id).select("-password");

    res.json(user);
  } catch (err) {
    console.log(err.message);
    res.status(500).send("Server error");
  }
});

module.exports = router;
