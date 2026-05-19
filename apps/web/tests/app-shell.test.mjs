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

test("app shell documents configurable API base URL", () => {
  const config = readFileSync(join(root, "lib/api-config.ts"), "utf8");
  const readme = readFileSync(join(root, "README.md"), "utf8");

  assert.match(config, /NEXT_PUBLIC_API_BASE_URL/);
  assert.match(config, /http:\/\/127\.0\.0\.1:8000/);
  assert.match(readme, /NEXT_PUBLIC_API_BASE_URL/);
});
