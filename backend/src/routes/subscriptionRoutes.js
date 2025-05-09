const express = require("express");
const subscriptionController = require("../controllers/subscriptionController");

const router = express.Router();

router.post("/", subscriptionController.subscribe);

module.exports = router;