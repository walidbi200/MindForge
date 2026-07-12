import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";

import { App } from "./App";
import "./index.css";

// Initialize Sentry for frontend error tracking.
// Disabled when VITE_SENTRY_DSN is not set (local dev).
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.MODE,
    tracesSampleRate: 0.1,
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
