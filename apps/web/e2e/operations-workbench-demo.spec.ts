import { expect, type Page, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../../..");
const detectionId = "det_fill_weight_gradual_drift";
const recommendationPath = `/recommendations?detection_id=${detectionId}`;

test("walks the simulator-backed Operations Workbench demo path", async ({ page }) => {
  resetDemoState();

  await page.goto("/");
  await expect(page.getByText("Simulator-backed demo data").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Greenville Demo Site" })).toBeVisible();
  await expect(page.getByText("Active detections")).toBeVisible();
  await expect(page.getByText("Pending recommendations")).toBeVisible();
  await expect(page.getByText("Severity", { exact: true })).toBeVisible();
  await expect(page.getByText("medium", { exact: true })).toBeVisible();

  await page.locator('a[href="/detections"]').first().click();
  await expect(page.getByRole("heading", { name: "Detections" })).toBeVisible();
  await expect(page.getByText("Process Sentinel detections from the local demo run")).toBeVisible();

  await page.locator(`a[href="/detections/${detectionId}"]`).click();
  await expect(page.getByRole("heading", { name: "Detection detail" })).toBeVisible();
  await expect(page.getByText("Status", { exact: true }).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Why this was flagged" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evidence timeline" })).toBeVisible();
  await expect(page.getByText("Recent fill weight average is higher than baseline")).toBeVisible();
  await expect(page.getByText("Recent quality checks are near the upper spec limit")).toBeVisible();

  await page.getByRole("link", { name: "Recommendation review" }).click();
  await expect(page.getByRole("heading", { name: "Recommendation review" })).toBeVisible();
  await expect(page.getByText("Recommendations are advisory decision support")).toBeVisible();
  await expect(page.getByText("Risk level", { exact: true })).toBeVisible();
  await recordDecision(page, "Approve", "approved");

  resetDemoState();
  await page.goto(recommendationPath);
  await expect(page.getByRole("heading", { name: "Recommendation review" })).toBeVisible();
  await recordDecision(page, "Reject", "rejected");

  resetDemoState();
  await page.goto(recommendationPath);
  await expect(page.getByRole("heading", { name: "Recommendation review" })).toBeVisible();
  await recordDecision(page, "Defer", "deferred");

  await page.locator(`a[href="/rca-capa-draft?detection_id=${detectionId}"]`).click();
  await expect(page.getByRole("heading", { name: "RCA/CAPA Draft" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Problem statement" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evidence summary" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Recommended containment" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "CAPA placeholder" })).toBeVisible();
  await expect(page.getByText("Human review", { exact: true })).toBeVisible();
  await expect(page.getByText("Required", { exact: true })).toBeVisible();
});

async function recordDecision(
  page: Page,
  action: "Approve" | "Reject" | "Defer",
  expectedDecision: "approved" | "rejected" | "deferred",
) {
  await page.getByLabel("Reviewer name").fill(`quality_engineer_${expectedDecision}`);
  await page
    .getByLabel("Decision reason")
    .fill(`Playwright smoke test recorded a ${expectedDecision} demo decision.`);
  await page.getByRole("button", { name: action }).click();

  const feedback = page.getByRole("status");
  await expect(feedback).toContainText(`Demo audit feedback: ${expectedDecision}`);
  await expect(feedback).toContainText(`Reviewer: quality_engineer_${expectedDecision}`);
  await expect(feedback).toContainText(`Updated status: ${expectedDecision}`);
  await expect(feedback).toContainText("not a validated production audit record");
}

function resetDemoState() {
  try {
    execFileSync("make", ["demo"], {
      cwd: repoRoot,
      encoding: "utf8",
      stdio: "pipe",
    });
  } catch (error) {
    const details =
      error instanceof Error && "stdout" in error && "stderr" in error
        ? `\nstdout:\n${String(error.stdout)}\nstderr:\n${String(error.stderr)}`
        : "";
    throw new Error(`Failed to prepare deterministic demo state with "make demo".${details}`);
  }
}
