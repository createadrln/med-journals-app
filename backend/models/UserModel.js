const db = require("../config/database");

const UserModel = {
  registerUser: (email, password, callback) => {
    const sql = "INSERT INTO users (email, password) VALUES (?, ?)";
    db.run(sql, [email, password], function (err) {
      callback(err, { id: this.lastID });
    });
  },
};

module.exports = UserModel;
