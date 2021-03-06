const express = require("express");
const router = express.Router();
const path = require("path");
const auth = require("../../middleware/auth");

// @route    POST api/profilepic/upload
// @desc     Upload profile pic
// @access   Private
router.post("/upload", auth, (req, res) => {
  if (req.files === null) {
    return res.status(400).json({ msg: "No file uploaded" });
  }

  const file = req.files.file;

  if (
    !(
      file.mimetype === "image/jpeg" ||
      file.mimetype === "image/png" ||
      file.mimetype === "image/jpg"
    )
  ) {
    return res
      .status(400)
      .json({ msg: "Invalid file type upload only png, jpg, jpeg" });
  }

  file.name = req.user.id + ".jpg";
  // switch (file.mimetype) {
  //   case "image/jpeg":
  //     file.name = req.user.id + "jpeg";
  //     break;

  //   case "image/png":
  //     file.name = req.user.id + "png";
  //     break;

  //   case "image/jpg":
  //     file.name = req.user.id + "jpg";
  //     break;
  // }

  const upload = path.resolve(
    __dirname,
    "..",
    "..",
    "..",
    "public",
    "uploads",
    file.name
  );

  file.mv(upload, (err) => {
    if (err) {
      console.error(err);
      return res.status(500).send(err);
    }

    res.json({ fileName: file.name, filePath: `/uploads/${file.name}` });
  });
});

module.exports = router;
