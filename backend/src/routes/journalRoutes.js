const express = require("express");
const router = express.Router();
const journalController = require("../controllers/journalController");

router.get("/", journalController.getJournals);

module.exports = router;
