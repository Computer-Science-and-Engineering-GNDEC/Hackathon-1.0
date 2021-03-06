require("dotenv").config();
const express = require("express");
const router = express.Router();
const { check, validationResult } = require("express-validator");

const auth = require("../../middleware/auth");
const User = require("../../models/User");
const Project = require("../../models/Project");

// @route    GET api/project
// @desc     Get All Projects
// @access   Public
router.get("/", async (req, res) => {
  try {
    const projects = await Project.find().populate("members", "fname");
    res.json(projects);
  } catch (err) {
    console.error(err.message);
    res.status(500).send("Server error");
  }
});

// @route    GET api/project/me
// @desc     Get All Projects of the user
// @access   Private
router.get("/me", auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    const projects = await Project.find({
      members: user.id,
    })
      .populate("members", ["fname", "lname", "zoho_mail", "date"])
      .populate("manager", "zoho_mail");

    res.json(projects);
  } catch (err) {
    console.error(err.message);
    res.status(500).send("Server error");
  }
});

// @route    POST api/project
// @desc     Post a project
// @access   Private
router.post(
  "/",
  [
    check("name", "Project name is required").not().isEmpty(),
    check("description", "Project description is required").not().isEmpty(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const {
      name,
      description,
      man,
      memb,
      img,
      github,
      projectLink,
      docLink,
    } = req.body;

    try {
      let p = await Project.findOne({ name });

      if (p) {
        return res
          .status(400)
          .json({ errors: [{ msg: "Project already exists" }] });
      }

      let user = await User.findOne({ zoho_mail: man });

      if (!user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "The manager does not exist" }] });
      }

      let manager = user._id;
      let members = [];
      members.push(manager);

      var i;
      for (i = 0; i < memb.length; i++) {
        const mem = await User.findOne({ zoho_mail: memb[i] });
        if (!mem) {
          return res
            .status(400)
            .json({ errors: [{ msg: `${members[i]} does not exist` }] });
        }

        members.push(mem._id);
      }

      const project = new Project({
        name,
        description,
        manager,
        members,
        img,
        github,
        projectLink,
        docLink,
      });

      let pro = await project.save();
      res.json(pro);
    } catch (err) {
      console.error(err.message);
      res.status(500).send("Server error");
    }
  }
);

// @route    POST api/project/b
// @desc     Post a Bussiness
// @access   Private
router.post(
  "/b",
  [
    check("name", "Project name is required").not().isEmpty(),
    check("description", "Project description is required").not().isEmpty(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { name, description, man, memb, img } = req.body;

    try {
      let p = await Project.findOne({ name });
      const project_class = "bussiness";

      if (p) {
        return res
          .status(400)
          .json({ errors: [{ msg: "Project already exists" }] });
      }

      let user = await User.findOne({ zoho_mail: man });

      if (!user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "The manager does not exist" }] });
      }

      let manager = user._id;
      let members = [];
      members.push(manager);

      var i;
      for (i = 0; i < memb.length; i++) {
        const mem = await User.findOne({ zoho_mail: memb[i] });
        if (!mem) {
          return res
            .status(400)
            .json({ errors: [{ msg: `${members[i]} does not exist` }] });
        }

        members.push(mem._id);
      }

      const project = new Project({
        name,
        description,
        manager,
        members,
        img,
        project_class,
      });

      let pro = await project.save();
      res.json(pro);
    } catch (err) {
      console.error(err.message);
      res.status(500).send("Server error");
    }
  }
);

// @route    POST api/project/:id
// @desc     Update a project
// @access   Private
router.put(
  "/:id",
  [
    check("name", "Project name is required").not().isEmpty(),
    check("description", "Project description is required").not().isEmpty(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const id = req.params.id;
    const {
      name,
      description,
      man,
      memb,
      img,
      github,
      projectLink,
      docLink,
    } = req.body;

    try {
      let p = await Project.findById(id);
      // console.log(p);

      if (!p) {
        return res.status(400).json({ errors: [{ msg: "Project not found" }] });
      }

      let user = await User.findOne({ zoho_mail: man });

      if (!user) {
        return res
          .status(400)
          .json({ errors: [{ msg: "The manager does not exist" }] });
      }

      let manager = user._id;
      let members = [];
      members.push(manager);

      var i;
      for (i = 0; i < memb.length; i++) {
        const mem = await User.findOne({ zoho_mail: memb[i] });
        if (!mem) {
          return res
            .status(400)
            .json({ errors: [{ msg: `${members[i]} does not exist` }] });
        }

        members.push(mem._id);
      }

      const project = {
        name,
        description,
        manager,
        members,
        img,
        github,
        projectLink,
        docLink,
      };

      p = await Project.findOneAndUpdate(id, { $set: project }, { new: true });
      console.log(p);
      res.json(p);
    } catch (err) {
      console.error(err.message);
      res.status(500).send("Server error");
    }
  }
);

module.exports = router;
