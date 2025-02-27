const app = require("./src/app");
const port = process.env.PORT || 3000;

// Start Server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

// Handle Shutdown
process.on("SIGINT", () => {
  console.log("Shutting down server...");
  process.exit(0);
});
