const db = require("../config/database");

const JournalModel = {
  getJournals: (filters, pagination, sorting, callback) => {
    let sql = `SELECT * FROM covid_research`;
    let countSql = `SELECT COUNT(*) AS totalCount FROM covid_research`;
    let queryParams = [];
    let whereClauses = [];

    // Filters
    if (filters.sources.length > 0) {
      const placeholders = filters.sources.map(() => "?").join(",");
      whereClauses.push(`Source IN (${placeholders})`);
      queryParams = queryParams.concat(filters.sources);
    }

    if (filters.title) {
      whereClauses.push(`title LIKE ?`);
      queryParams.push(`%${filters.title}%`);
    }

    if (filters.keyword) {
      whereClauses.push(`keywords LIKE ?`);
      queryParams.push(`%${filters.keyword}%`);
    }

    if (whereClauses.length > 0) {
      sql += ` WHERE ${whereClauses.join(" AND ")}`;
      countSql += ` WHERE ${whereClauses.join(" AND ")}`;
    }

    // Sorting
    sql += ` ORDER BY ${sorting.column} ${sorting.order}`;

    // Pagination
    sql += ` LIMIT ? OFFSET ?`;
    queryParams.push(pagination.pageSize, pagination.offset);

    // Get total count
    db.get(
      countSql,
      queryParams.slice(0, queryParams.length - 2),
      (err, countRow) => {
        if (err) return callback(err, null);

        const totalCount = countRow.totalCount;
        const totalPages = Math.ceil(totalCount / pagination.pageSize);

        // Fetch journal data
        db.all(sql, queryParams, (err, rows) => {
          if (err) return callback(err, null);
          callback(null, {
            page: pagination.page,
            pageSize: pagination.pageSize,
            totalCount,
            totalPages,
            data: rows,
          });
        });
      }
    );
  },
};

module.exports = JournalModel;
