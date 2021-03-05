const mongoose = require("mongoose");

const projectSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
  },
  description: {
    type: String,
    required: true,
  },
  manager: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "user",
  },
  img: {
    type: String,
  },
  members: [
    {
      type: mongoose.Schema.Types.ObjectId,
      ref: "user",
    },
  ],
  github: {
    type: String,
  },
  projectLink: {
    type: String,
  },
  docLink: {
    type: String,
  },
  project_class: {
    type: String,
    default: "project",
  },
});

module.exports = Project = mongoose.model("project", projectSchema);
