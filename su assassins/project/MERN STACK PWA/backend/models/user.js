const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  zoho_mail: {
    type: String,
    required: true,
    unique: true,
    trim: true,
  },
  fname: {
    type: String,
    required: true,
  },
  lname: {
    type: String,
    required: true,
  },
  contact: {
    type: String,
    required: true,
  },
  password: {
    type: String,
    required: true,
    minlength: 8,
  },
  gender: {
    type: String,
    required: true,
  },
  role: {
    type: Number,
    default: 1,
  },
  profileImage: {
    type: String,
    required: false,
  },
  date: {
    type: Date,
    default: Date.now,
  },
  resetPasswordToken: {
    type: String,
  },
  resetPasswordExpires: {
    type: Date,
  },
});

module.exports = User = mongoose.model("user", userSchema);
