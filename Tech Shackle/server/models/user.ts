import mongoose from 'mongoose';
import bcrypt from 'bcrypt';
import { threadId } from 'node:worker_threads';
const crypto = require('crypto');

/* Required using mongo hook with TS */
interface IUser extends mongoose.Document {
  passwordResetToken: any;
  passwordResetExpires: number;
  email: string;
  name?: string;
  password: string;
  profileImageURL?: string;
  isAdmin?: boolean;
}

const userSchema = new mongoose.Schema<IUser>({
  email: {
    type: String,
    required: true,
    unique: true,
  },
  name: {
    type: String,
  },
  password: {
    type: String,
    required: true,
  },
  profileImageURL: {
    type: String,
  },
  isAdmin: {
    type: Boolean,
    required: true,
    default: false,
  },
  passwordChangedAt: Date,
  passwordResetToken : String,
  passwordResetExpires : Date
});

userSchema.pre<IUser>('save', async function (next) {
  try {
    if (!this.isModified('password')) {
      return next();
    }

    const hashedPassword = await bcrypt.hash(this.password, 10);
    this.password = hashedPassword;

    /* Since it is asynchronous, we need to specify when to move on */
    return next();
  } catch (error) {
    return next(error);
  }
});

userSchema.methods.comparePassword = async function (enteredPassword, next) {
  try {
    const isMatch = await bcrypt.compare(enteredPassword, this.password);
    return isMatch;
  } catch (error) {
    next(error);
  }
};

userSchema.methods.createPasswordResetToken = function() {
  const resetToken = crypto.randomBytes(32).toString('hex');

  console.log({ resetToken }, this.passwordResetToken);

  this.passwordResetToken = crypto.createHash('sha256').update(resetToken).digest('hex');
  this.passwordResetExpires = Date.now() + 10 * 60 * 1000;
  return resetToken;
};

const User = mongoose.model('User', userSchema);

// export default User;
module.exports = User;
