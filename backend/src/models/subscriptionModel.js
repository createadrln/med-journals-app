const fs = require("fs");
const path = require("path");

const filePath = path.join(__dirname, "../../subscribers.txt");

exports.saveEmail = (email, callback) => {
  const entry = `${email}\n`;
  fs.appendFile(filePath, entry, callback);
};