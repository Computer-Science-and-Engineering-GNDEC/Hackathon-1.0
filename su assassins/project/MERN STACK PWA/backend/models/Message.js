const mongoose = require("mongoose");

const whatsappSchema = new mongoose.Schema({
  room: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "project",
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "user",
  },
  message: { type: String },
  name: { type: String },
  timestamp: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model("messagecontents", whatsappSchema);
