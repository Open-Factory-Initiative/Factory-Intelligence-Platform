import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import test from "node:test";

const root = fileURLToPath(new URL("..", import.meta.url));
const client = readFileSync(join(root, "lib/api-client.ts"), "utf8");

const requiredEndpoints = [
  "/health",
  "/sites",
  "/areas",
  "/equipment",
  "/batches",
  "/sentinel/detections",
  "/sentinel/detections/${encodeURIComponent(detectionId)}",
  "/sentinel/detections/${encodeURIComponent(detectionId)}/evidence",
  "/recommendations",
  "/recommendations/${encodeURIComponent(recommendationId)}",
  "/recommendations/${encodeURIComponent(recommendationId)}/${decision}",
  "/reports/rca-capa-drafts/${encodeURIComponent(detectionId)}",
];

test("typed workbench API client covers demo endpoints", () => {
  for (const endpoint of requiredEndpoints) {
    assert.ok(client.includes(endpoint), `missing endpoint: ${endpoint}`);
  }

  assert.match(client, /getHealth/);
  assert.match(client, /listSites/);
  assert.match(client, /listAreas/);
  assert.match(client, /listEquipment/);
  assert.match(client, /listBatches/);
  assert.match(client, /listDetections/);
  assert.match(client, /getDetection/);
  assert.match(client, /listDetectionEvidence/);
  assert.match(client, /listRecommendations/);
  assert.match(client, /getRecommendation/);
  assert.match(client, /approveRecommendation/);
  assert.match(client, /rejectRecommendation/);
  assert.match(client, /deferRecommendation/);
  assert.match(client, /getRcaCapaDraft/);
});

test("API client posts governed recommendation decisions as JSON", () => {
  assert.match(client, /method: "POST"/);
  assert.match(client, /body: JSON.stringify\(request\)/);
  assert.match(client, /"content-type": "application\/json"/);
});

test("API errors and route loading states are user-visible", async () => {
  assert.match(client, /formatApiError/);
  assert.match(client, /ApiClientError/);

  const stateComponent = readFileSync(join(root, "app/components/demo-state.tsx"), "utf8");
  assert.match(stateComponent, /API connection issue/);
  assert.match(stateComponent, /aria-busy="true"/);

  await Promise.all([
    access(join(root, "app/loading.tsx")),
    access(join(root, "app/detections/loading.tsx")),
    access(join(root, "app/recommendations/loading.tsx")),
    access(join(root, "app/rca-capa-draft/loading.tsx")),
  ]);
});
