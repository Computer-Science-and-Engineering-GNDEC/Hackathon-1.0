require("dotenv").config();
const express = require("express");
const router = express.Router();
const { check, validationResult } = require("express-validator");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const User = require("../../models/User");

// @route    POST api/users
// @desc     Register user
// @access   Public
router.post(
  "/",
  [
    check("zoho_mail", "Please input a valid zoho mail").isEmail(),
    check("fname", "First name is srequired").not().isEmpty(),
    check("lname", "Last name is srequired").not().isEmpty(),
    check("contact", "Contact no. is required and should be valid")
      .isLength(10)
      .not()
      .isEmpty(),
    check("gender", "Gender is required").not().isEmpty(),
    check(
      "password",
      "Please enter a password with 8 or more characters"
    ).isLength({ min: 8 }),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { zoho_mail, fname, lname, contact, gender, password } = req.body;

    try {
      if (!/^([a-z0-9_\.-]+)@(gmail)\.(com)$/.test(zoho_mail)) {
        return res
          .status(400)
          .json({ errors: [{ msg: "Enter a valid gmail" }] });
      }

      let user = await User.findOne({ zoho_mail });

      if (user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "User already exist" }] });
      }

      user = new User({
        zoho_mail,
        fname,
        lname,
        contact,
        gender,
        password,
      });

      const salt = await bcrypt.genSalt(10);
      user.password = await bcrypt.hash(password, salt);

      await user.save();

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

router.post("/tokenIsValid", async (req, res) => {
  try {
    const token = req.header("x-auth-token");
    if (!token) return res.json(false);

    const verified = jwt.verify(token, process.env.JWT_SECRET);
    if (!verified) return res.json(false);

    const user = await User.findById(verified.id);
    if (!user) return res.json(false);

    return res.json(true);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
