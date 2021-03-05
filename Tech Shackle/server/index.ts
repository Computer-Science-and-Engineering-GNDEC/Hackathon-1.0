// Load env variables
require('dotenv').config();

import express from 'express';
import cors from 'cors'

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`Server started on PORT ${PORT}`));
