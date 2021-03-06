require("dotenv").config();
const express = require("express");
const router = express.Router();
const mongoose = require("mongoose");
const Pusher = require("pusher");
const Message = require("../../models/Message");
const auth = require("../../middleware/auth");
const User = require("../../models/User");
const Project = require("../../models/Project");

const Messages = require("../../models/Message");

const pusher = new Pusher({
  appId: "1114801",
  key: "9b4bb56b8cb856641dae",
  secret: "d8d5790b8f77b5a05ed0",
  cluster: "ap2",
  useTLS: true,
});

//Pusher
const db = mongoose.connection;

db.once("open", () => {
  console.log("DB connected");

  const msgCollection = db.collection("messagecontents");
  const changeStream = msgCollection.watch();

  changeStream.on("change", (change) => {
    if (change.operationType === "insert") {
      const messageDetails = change.fullDocument;
      pusher.trigger("message", "inserted", {
        room: messageDetails.room,
        name: messageDetails.name,
        user: messageDetails.user,
        message: messageDetails.message,
        timestamp: messageDetails.timestamp,
      });
    } else {
      console.log("Error triggering Pusher");
    }
  });
});

// @route    GET api/messages
// @desc     Test Route
// @access   Public
router.get("/", (req, res) => res.status(200).send("hello world"));

// @route    GET api/messages/sync
// @desc     Sync Message
// @access   Public
router.get("/sync", async (req, res) => {
  try {
    const messages = await Message.find().sort({ timestamp: 1 });
    res.send(messages);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ errors: [{ msg: "Server Error" }] });
  }
});

// @route    GET api/messages/:id
// @desc     Sync Message
// @access   Public
router.get("/:id", auth, async (req, res) => {
  try {
    const messages = await Message.find({ room: req.params.id }).sort({
      timestamp: 1,
    });
    res.json(messages);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ errors: [{ msg: "Server Error" }] });
  }
});

// @route    GET api/messages/new
// @desc     New Message
// @access   Private
router.post("/new/:id", auth, async (req, res) => {
  // const dbMessage = req.body;
  // Messages.create(dbMessage, (err, data) => {
  //   if (err) {
  //     res.status(500).send(err);
  //   } else {
  //     res.status(201).send(data);
  //   }
  // });

  const message = req.body.message;
  try {
    const user = await User.findById(req.user.id).select("-password");

    const newMessage = new Message({
      room: req.params.id,
      user: user.id,
      message: message,
      name: user.fname,
    });

    const msgs = await newMessage.save();
    res.json(msgs);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ errors: [{ msg: "Server Error" }] });
  }
});

module.exports = router;
