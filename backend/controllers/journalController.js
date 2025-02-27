const JournalModel = require("../models/JournalModel");

exports.getJournals = (req, res) => {
  const {
    page = 1,
    pageSize = 10,
    source,
    title,
    keyword,
    sort = "pub_date",
    order = "DESC",
  } = req.query;

  const pagination = {
    page: parseInt(page, 10),
    pageSize: parseInt(pageSize, 10),
    offset: (parseInt(page, 10) - 1) * parseInt(pageSize, 10),
  };

  const filters = {
    sources: source ? JSON.parse(source) : [],
    title,
    keyword,
  };

  const sorting = {
    column: ["pub_date", "title"].includes(sort) ? sort : "pub_date",
    order: order.toUpperCase() === "ASC" ? "ASC" : "DESC",
  };

  JournalModel.getJournals(filters, pagination, sorting, (err, result) => {
    if (err) {
      return res.status(500).send({ error: err.message });
    }
    res.status(200).send(result);
  });
};
