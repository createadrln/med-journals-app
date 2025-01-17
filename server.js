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
app.get('/journals', (req, res) => {
  const { page = 1, pageSize = 10, source, title } = req.query;
  const pageValue = parseInt(page, 10);
  const pageSizeValue = parseInt(pageSize, 10);

  if (isNaN(pageValue) || pageValue <= 0) {
      return res.status(400).send({ error: "Invalid 'page' parameter. It must be a positive integer." });
  }
  if (isNaN(pageSizeValue) || pageSizeValue <= 0) {
      return res.status(400).send({ error: "Invalid 'pageSize' parameter. It must be a positive integer." });
  }

  const offset = (pageValue - 1) * pageSizeValue;

  // Parse source as an array if provided
  let sourceArray = [];
  if (source) {
      try {
          sourceArray = JSON.parse(source); // Expecting source to be a JSON stringified array
          if (!Array.isArray(sourceArray)) {
              return res.status(400).send({ error: "'source' must be an array of strings." });
          }
      } catch (err) {
          return res.status(400).send({ error: "'source' must be a valid JSON stringified array." });
      }
  }

  // Initialize query and parameters
  let countSql = `SELECT COUNT(*) AS totalCount FROM covid_journals_data`;
  let dataSql = `SELECT * FROM covid_journals_data`;
  let queryParams = [];

  // Build WHERE clause
  let whereClauses = [];

  // Add source filter
  if (sourceArray.length > 0) {
      const placeholders = sourceArray.map(() => '?').join(', ');
      whereClauses.push(`Source IN (${placeholders})`);
      queryParams = queryParams.concat(sourceArray);
  }

  // Add title filter
  if (title) {
      whereClauses.push(`title LIKE ?`);
      queryParams.push(`%${title}%`); // Add wildcards for partial matching
  }

  // Combine WHERE clauses
  if (whereClauses.length > 0) {
      countSql += ` WHERE ${whereClauses.join(' AND ')}`;
      dataSql += ` WHERE ${whereClauses.join(' AND ')}`;
  }

  dataSql += ` LIMIT ? OFFSET ?`;
  // dataSql += ` ORDER BY RANDOM() LIMIT ? OFFSET ?`;
  queryParams.push(pageSizeValue, offset);

  // Execute the count query
  db.get(countSql, queryParams.slice(0, queryParams.length - 2), (countErr, countRow) => {
      if (countErr) {
          return res.status(500).send({ error: countErr.message });
      }

      const totalCount = countRow.totalCount;
      const totalPages = Math.ceil(totalCount / pageSizeValue);

      // Execute the data query
      db.all(dataSql, queryParams, (dataErr, dataRows) => {
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
