const subscriptionModel = require("../models/subscriptionModel");

exports.subscribe = (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ error: "Email is required" });
  }

  subscriptionModel.saveEmail(email, (err) => {
    if (err) {
      console.error("Error saving email:", err);
      return res.status(500).json({ error: "Failed to save email" });
    }

    res.status(200).json({ message: "Subscription successful" });
  });
};