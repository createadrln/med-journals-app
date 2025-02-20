const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");

const journalRoutes = require("./routes/journalRoutes");
const keywordRoutes = require("./routes/keywordRoutes");
const userRoutes = require("./routes/userRoutes");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// API Routes
app.use("/journals", journalRoutes);
app.use("/keywords", keywordRoutes);
app.use("/users", userRoutes);

module.exports = app;
