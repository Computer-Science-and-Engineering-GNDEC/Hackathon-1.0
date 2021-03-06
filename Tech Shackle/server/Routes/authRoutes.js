const express = require("express");

const Router = express.Router();

const authHandler = require("./../Handlers/authHandler");

Router.post("/signup", authHandler.signup);
Router.post("/login", authHandler.login);
Router.post("/forgotPassword", authHandler.forgotPassword);

module.exports = Router;
