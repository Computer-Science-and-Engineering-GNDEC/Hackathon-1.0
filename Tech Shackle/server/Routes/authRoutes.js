const express = require('express');

const Router = express.Router();

const authHandler = require('./../Handlers/authHandler');
const { deleteDocument } = require('../Handlers/delete');

Router.post('/signup', authHandler.signup).delete('/:id', deleteDocument);

module.exports = Router;
