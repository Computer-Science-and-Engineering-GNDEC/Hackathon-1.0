require("dotenv").config();
const express = require("express");
const fileUpload = require("express-fileupload");
const connectDB = require("./config/db");
const cors = require("cors");

const app = express();

//Init Middleware
app.use(express.json());
app.use(fileUpload());
app.use(cors());

//Connect Database
connectDB();

//Define Routes
app.use("/api/users", require("./routes/api/users"));
app.use("/api/auth", require("./routes/api/auth"));
app.use("/api/project", require("./routes/api/project"));
app.use("/api/messages", require("./routes/api/messages"));
app.use("/api/profilepic", require("./routes/api/profilePic"));

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log("Server is running on port:", PORT));
