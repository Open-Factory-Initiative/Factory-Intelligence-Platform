import { defineConfig } from "@playwright/test";
import path from "node:path";

const webRoot = __dirname;
const repoRoot = path.resolve(__dirname, "../..");

export default defineConfig({
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  reporter: [["list"]],
  testDir: "./e2e",
  timeout: 90_000,
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command:
        "make api EVENTS_STORE=.local/storage/fill_weight_drift_demo_events.jsonl SENTINEL_STATE_DIR=.local/storage/fill_weight_drift_demo_sentinel",
      cwd: repoRoot,
      env: {
        FACTORY_API_CORS_ORIGINS: "http://127.0.0.1:3000",
      },
      reuseExistingServer: false,
      timeout: 30_000,
      url: "http://127.0.0.1:8000/health",
    },
    {
      command: "npm run dev",
      cwd: webRoot,
      env: {
        NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8000",
      },
      reuseExistingServer: false,
      timeout: 45_000,
      url: "http://127.0.0.1:3000",
    },
  ],
  workers: 1,
});
