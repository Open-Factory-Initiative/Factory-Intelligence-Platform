import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import test from "node:test";

const root = fileURLToPath(new URL("..", import.meta.url));

const requiredRoutes = [
  "app/page.tsx",
  "app/detections/page.tsx",
  "app/detections/[detectionId]/page.tsx",
  "app/recommendations/page.tsx",
  "app/rca-capa-draft/page.tsx",
];

test("workbench placeholder routes exist", async () => {
  await Promise.all(requiredRoutes.map((route) => access(join(root, route))));
});

test("navigation includes the required demo routes", () => {
  const layout = readFileSync(join(root, "app/layout.tsx"), "utf8");

  assert.match(layout, /Overview/);
  assert.match(layout, /Detections/);
  assert.match(layout, /Recommendations/);
  assert.match(layout, /RCA\/CAPA Draft/);
});

test("overview page contains manufacturer demo dashboard content", () => {
  const overview = readFileSync(join(root, "app/page.tsx"), "utf8");

  assert.match(overview, /Current demo context/);
  assert.match(overview, /Active detections/);
  assert.match(overview, /Pending recommendations/);
  assert.match(overview, /Most important detection/);
  assert.match(overview, /Open detection/);
  assert.match(overview, /selectImportantDetection/);
});

test("detections pages contain list and detail content", () => {
  const list = readFileSync(join(root, "app/detections/page.tsx"), "utf8");
  const detail = readFileSync(join(root, "app/detections/[detectionId]/page.tsx"), "utf8");

  assert.match(list, /Process Sentinel detections from the local demo run/);
  assert.match(list, /detection.summary/);
  assert.match(list, /detection.severity/);
  assert.match(list, /detection.confidence/);
  assert.match(list, /detection.status/);
  assert.match(list, /formatTimeWindow/);
  assert.match(list, /related_work_order_id/);
  assert.match(list, /related_asset_ids/);
  assert.match(list, /Open detection/);
  assert.match(detail, /Detection detail/);
  assert.match(detail, /getDetection/);
});

test("app shell documents configurable API base URL", () => {
  const config = readFileSync(join(root, "lib/api-config.ts"), "utf8");
  const client = readFileSync(join(root, "lib/api-client.ts"), "utf8");
  const readme = readFileSync(join(root, "README.md"), "utf8");

  assert.match(config, /NEXT_PUBLIC_API_BASE_URL/);
  assert.match(client, /apiBaseUrl/);
  assert.match(config, /http:\/\/127\.0\.0\.1:8000/);
  assert.match(readme, /NEXT_PUBLIC_API_BASE_URL/);
});
