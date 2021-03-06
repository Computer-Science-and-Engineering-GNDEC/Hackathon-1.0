const express = require("express");
const authHandler = require("./../Handlers/authHandler");
const Router = express.Router();
const { deleteDocument } = require("../Handlers/delete");

Router.post("/signup", authHandler.signup);
Router.post("/login", authHandler.login);
Router.post("/forgotPassword", authHandler.forgotPassword);
Router.post("/signup", authHandler.signup).delete("/:id", deleteDocument);

module.exports = Router;
