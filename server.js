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
// app.get("/journals", (req, res) => {
//   const {
//     page = 1,
//     pageSize = 10,
//     source,
//     title,
//     sort = "date",
//     order = "DESC",
//   } = req.query;

//   let sql = `SELECT * FROM covid_research`;
//   const params = [];

//   // Filter by Source (Array of Strings)
//   if (source) {
//     const sources = JSON.parse(source);
//     const placeholders = sources.map(() => "?").join(", ");
//     sql += ` WHERE source IN (${placeholders})`;
//     params.push(...sources);
//   }

//   // Filter by Title (Partial Match)
//   if (title) {
//     sql += source ? " AND" : " WHERE";
//     sql += ` title LIKE ?`;
//     params.push(`%${title}%`);
//   }

//   // Sorting by Date or Title
//   const validSortColumns = ["pub_date", "title"];
//   const sortColumn = validSortColumns.includes(sort) ? sort : "pub_date";

//   const orderDirection = order.toUpperCase() === "ASC" ? "ASC" : "DESC";
//   sql += ` ORDER BY ${sortColumn} ${orderDirection}`;

//   // Pagination
//   sql += ` LIMIT ? OFFSET ?`;
//   params.push(parseInt(pageSize), (parseInt(page) - 1) * parseInt(pageSize));

//   // Execute Query
//   db.all(sql, params, (err, rows) => {
//     if (err) {
//       return res.status(500).send({ error: err.message });
//     }

//     // Count total records for pagination
//     db.get(
//       `SELECT COUNT(*) as total FROM covid_research`,
//       [],
//       (err, result) => {
//         if (err) {
//           return res.status(500).send({ error: err.message });
//         }

//         res.status(200).send({
//           totalRecords: result.total,
//           totalPages: Math.ceil(result.total / pageSize),
//           data: rows,
//         });
//       }
//     );
//   });
// });

app.get("/journals", (req, res) => {
  const {
    page = 1,
    pageSize = 10,
    source,
    title,
    sort = "pub_date",
    order = "DESC",
  } = req.query;

  const pageValue = parseInt(page, 10);
  const pageSizeValue = parseInt(pageSize, 10);

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

  // Parse source as an array if provided
  let sourceArray = [];
  if (source) {
    try {
      sourceArray = JSON.parse(source); // Expecting source to be a JSON stringified array
      if (!Array.isArray(sourceArray)) {
        return res
          .status(400)
          .send({ error: "'source' must be an array of strings." });
      }
    } catch (err) {
      return res
        .status(400)
        .send({ error: "'source' must be a valid JSON stringified array." });
    }
  }

  // Initialize query and parameters
  let countSql = `SELECT COUNT(*) AS totalCount FROM covid_research`;
  let dataSql = `SELECT * FROM covid_research`;
  let queryParams = [];

  // Build WHERE clause
  let whereClauses = [];

  // Add source filter
  if (sourceArray.length > 0) {
    const placeholders = sourceArray.map(() => "?").join(", ");
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
    countSql += ` WHERE ${whereClauses.join(" AND ")}`;
    dataSql += ` WHERE ${whereClauses.join(" AND ")}`;
  }

  // Sorting by Date or Title
  const validSortColumns = ["pub_date", "title"];
  const sortColumn = validSortColumns.includes(sort) ? sort : "pub_date";

  const orderDirection = order.toUpperCase() === "ASC" ? "ASC" : "DESC";
  dataSql += ` ORDER BY ${sortColumn} ${orderDirection}`;

  dataSql += ` LIMIT ? OFFSET ?`;
  queryParams.push(pageSizeValue, offset);

  // Execute the count query
  db.get(
    countSql,
    queryParams.slice(0, queryParams.length - 2),
    (countErr, countRow) => {
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
    }
  );
});

// Get all keywords
app.get("/keywords", (req, res) => {
  const { keyword, article_id } = req.query;
  let sql = "SELECT * FROM covid_research_keywords WHERE 1=1";
  const params = [];

  if (keyword) {
    sql += " AND keyword LIKE ?";
    params.push(`%${keyword}%`);
  }

  if (article_id) {
    sql += " AND article_id = ?";
    params.push(article_id);
  }

  db.all(sql, params, (err, rows) => {
    if (err) {
      return res.status(500).send({ error: err.message });
    }
    res.status(200).send(rows);
  });
});

// Add a new keyword
app.post("/keywords", (req, res) => {
  const { keyword, article_id } = req.body;

  if (!keyword || !article_id) {
    return res
      .status(400)
      .send({ error: "Both 'keyword' and 'article_id' are required." });
  }

  const sql =
    "INSERT INTO covid_research_keywords (keyword, article_id) VALUES (?, ?)";
  const params = [keyword, article_id];

  db.run(sql, params, function (err) {
    if (err) {
      return res.status(500).send({ error: err.message });
    }
    res.status(201).send({ id: this.lastID, keyword, article_id });
  });
});

// Update an existing keyword
app.put("/keywords/:id", (req, res) => {
  const { id } = req.params;
  const { keyword, article_id } = req.body;

  if (!keyword || !article_id) {
    return res
      .status(400)
      .send({ error: "Both 'keyword' and 'article_id' are required." });
  }

  const sql =
    "UPDATE covid_research_keywords SET keyword = ?, article_id = ? WHERE id = ?";
  const params = [keyword, article_id, id];

  db.run(sql, params, function (err) {
    if (err) {
      return res.status(500).send({ error: err.message });
    }
    if (this.changes === 0) {
      return res.status(404).send({ error: "Keyword not found." });
    }
    res.status(200).send({ id, keyword, article_id });
  });
});

// Delete a keyword
app.delete("/keywords/:id", (req, res) => {
  const { id } = req.params;

  const sql = "DELETE FROM covid_research_keywords WHERE id = ?";
  const params = [id];

  db.run(sql, params, function (err) {
    if (err) {
      return res.status(500).send({ error: err.message });
    }
    if (this.changes === 0) {
      return res.status(404).send({ error: "Keyword not found." });
    }
    res.status(200).send({ message: "Keyword deleted successfully.", id });
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
