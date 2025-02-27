const KeywordModel = require("../models/KeywordModel");

exports.getKeywords = (req, res) => {
  const { keyword, article_id } = req.query;
  const filters = { keyword, article_id };

  KeywordModel.getAll(filters, (err, rows) => {
    if (err) return res.status(500).send({ error: err.message });

    const keywords = [];
    rows.forEach((row) => {
      keywords.push(row.keyword);
    });

    const counts = keywords.sort().reduce(
      (acc, value) => ({
        ...acc,
        [value]: (acc[value] || 0) + 1,
      }),
      {}
    );

    res.status(200).send(counts);
  });
};

exports.addKeyword = (req, res) => {
  const { keyword, article_id } = req.body;

  if (!keyword || !article_id) {
    return res
      .status(400)
      .send({ error: "Both 'keyword' and 'article_id' are required." });
  }

  KeywordModel.create({ keyword, article_id }, (err, result) => {
    if (err) return res.status(500).send({ error: err.message });
    res.status(201).send(result);
  });
};

exports.updateKeyword = (req, res) => {
  const { id } = req.params;
  const { keyword, article_id } = req.body;

  if (!keyword || !article_id) {
    return res
      .status(400)
      .send({ error: "Both 'keyword' and 'article_id' are required." });
  }

  KeywordModel.update({ id, keyword, article_id }, (err, result) => {
    if (err) return res.status(500).send({ error: err.message });
    res.status(200).send(result);
  });
};

exports.deleteKeyword = (req, res) => {
  const { id } = req.params;

  KeywordModel.delete(id, (err, result) => {
    if (err) return res.status(500).send({ error: err.message });
    res.status(200).send(result);
  });
};
