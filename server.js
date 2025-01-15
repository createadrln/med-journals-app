const express = require("express");
const bodyParser = require("body-parser");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const port = process.env.PORT || 3000;
const db = new sqlite3.Database("./databases/CovidData.db", (err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log("Connected to the SQlite database.");
});

const cors = require("cors");
app.use(cors());

app.use(bodyParser.json());

// Define API endpoints

// Get all journals
app.get("/journals", (req, res) => {
  const { page, pageSize, source } = req.query;
  const pageValue = parseInt(page, 10);
  const pageSizeValue = parseInt(pageSize, 10);

  // Validate page and pageSize parameters
  if (isNaN(pageValue) || pageValue <= 0) {
    return res.status(400).send({
      error: "Invalid 'page' parameter. It must be a positive integer.",
    });
  }
  if (isNaN(pageSizeValue) || pageSizeValue <= 0) {
    return res.status(400).send({
      error: "Invalid 'pageSize' parameter. It must be a positive integer.",
    });
  }

  const offset = (pageValue - 1) * pageSizeValue;

  // Query to count total rows
  let countSql = `SELECT COUNT(*) AS totalCount FROM covid_journals_data`;
  const countParams = [];

  // Add WHERE clause if source is provided
  if (source) {
    countSql += ` WHERE Source = ?`;
    countParams.push(source);
  }

  // Query to fetch paginated data
  let dataSql = `SELECT * FROM covid_journals_data`;
  const dataParams = [];

  if (source) {
    dataSql += ` WHERE Source = ?`;
    dataParams.push(source);
  }

  dataSql += ` ORDER BY RANDOM() LIMIT ? OFFSET ?`;
  dataParams.push(pageSizeValue, offset);

  // Execute the count query first
  db.get(countSql, countParams, (countErr, countRow) => {
    if (countErr) {
      return res.status(500).send({ error: countErr.message });
    }

    const totalCount = countRow.totalCount;
    const totalPages = Math.ceil(totalCount / pageSizeValue);

    // Execute the data query next
    db.all(dataSql, dataParams, (dataErr, dataRows) => {
      if (dataErr) {
        return res.status(500).send({ error: dataErr.message });
      }

      res.status(200).send({
        page: pageValue,
        pageSize: pageSizeValue,
        totalPages: totalPages,
        totalCount: totalCount,
        data: dataRows,
      });
    });
  });
});

// Register a new user
app.post("/users/register", (req, res) => {
  const { email, password } = req.body;
  const sql = `INSERT INTO users (email, password) VALUES (?, ?)`;
  db.run(sql, [email, password], function (err) {
    if (err) {
      return res.status(400).send({ error: err.message });
    }
    res.status(201).send({ id: this.lastID });
  });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

// Handle shutdown
process.on("SIGINT", () => {
  db.close(() => {
    console.log("Database connection closed.");
    process.exit(0);
  });
});
