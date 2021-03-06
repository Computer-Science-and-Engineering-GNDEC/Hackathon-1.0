import mongoose from 'mongoose';
// const mongoose = require('mongoose')

mongoose.set('debug', true);

mongoose.Promise = Promise;

const DB_URI: string = process.env.DB_URI!;

mongoose
  .connect(DB_URI, {
    keepAlive: true,
    useUnifiedTopology: true,
    useNewUrlParser: true,
    useCreateIndex: true,
  })
  .then(() => console.log('connected to mongoose DB'))
  .catch((e: Error) => console.log(e));

module.exports.User = require('./user');
