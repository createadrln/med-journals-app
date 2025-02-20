const UserModel = require("../models/UserModel");

exports.registerUser = (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res
      .status(400)
      .send({ error: "Both 'email' and 'password' are required." });
  }

  UserModel.register({ email, password }, (err, result) => {
    if (err) return res.status(400).send({ error: err.message });
    res.status(201).send(result);
  });
};
