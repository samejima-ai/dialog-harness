import { expect, test } from "@playwright/test";

test("ルートページが表示される", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "ケロぴの森" })).toBeVisible();
});
