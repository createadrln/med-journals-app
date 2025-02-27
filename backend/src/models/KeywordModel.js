const db = require("../config/database");

const KeywordModel = {
  getAll: (filters, callback) => {
    let sql = "SELECT keyword FROM covid_research_keywords";
    const params = [];

    if (filters.keyword) {
      sql += " AND keyword LIKE ?";
      params.push(`%${filters.keyword}%`);
    }

    if (filters.article_id) {
      sql += " AND id = ?";
      params.push(filters.article_id);
    }

    db.all(sql, params, (err, rows) => {
      if (err) return callback(err, null);
      callback(null, rows);
    });
  },

  create: ({ keyword, article_id }, callback) => {
    const sql =
      "INSERT INTO covid_research_keywords (keyword, article_id) VALUES (?, ?)";
    db.run(sql, [keyword, article_id], function (err) {
      if (err) return callback(err, null);
      callback(null, { id: this.lastID, keyword, article_id });
    });
  },

  update: ({ id, keyword, article_id }, callback) => {
    const sql =
      "UPDATE covid_research_keywords SET keyword = ?, article_id = ? WHERE id = ?";
    db.run(sql, [keyword, article_id, id], function (err) {
      if (err) return callback(err, null);
      callback(null, { id, keyword, article_id });
    });
  },

  delete: (id, callback) => {
    const sql = "DELETE FROM covid_research_keywords WHERE id = ?";
    db.run(sql, [id], function (err) {
      if (err) return callback(err, null);
      callback(null, { message: "Keyword deleted successfully.", id });
    });
  },
};

module.exports = KeywordModel;
