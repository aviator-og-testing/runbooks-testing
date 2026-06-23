const path = require("path");
const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");

const app = express();
const PORT = process.env.PORT || 3000;
const API_TARGET = process.env.API_TARGET || "http://localhost:8000";

// Proxy /api calls to the Python backend so the browser can use same-origin requests.
app.use(
  "/api",
  createProxyMiddleware({
    target: API_TARGET,
    changeOrigin: true,
    pathRewrite: { "^/api": "" },
  }),
);

app.use(express.static(path.join(__dirname, "src")));

app.listen(PORT, () => {
  console.log(`frontend listening on ${PORT}, proxying /api -> ${API_TARGET}`);
});
