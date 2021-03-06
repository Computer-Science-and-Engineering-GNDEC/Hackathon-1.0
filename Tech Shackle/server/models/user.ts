import mongoose from 'mongoose';
import bcrypt from 'bcrypt';

/* Required using mongo hook with TS */
interface IUser extends mongoose.Document {
  email: string;
  name?: string;
  password: string;
  profileImageURL?: string;
  role: 'student' | 'teahcer' | 'admin';
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
  role: {
    type: String,
    required: true,
    default: 'student'
  }
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

const User = mongoose.model('User', userSchema);

// export default User;
module.exports = User;
