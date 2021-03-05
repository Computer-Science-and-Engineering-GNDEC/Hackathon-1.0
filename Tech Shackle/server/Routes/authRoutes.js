const express = require('express');

const Router = express.Router();

const authHandler = require('./../Handlers/authHandler');

Router.post('/signup', authHandler.signup);

module.exports = Router;