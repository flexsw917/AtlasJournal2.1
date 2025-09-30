import { test, expect, Page } from "@playwright/test";

const user = {
  email: `tester+${Date.now()}@zellalite.dev`,
  password: "Playwright123"
};

async function signupAndLogin(page: Page) {
  await page.goto("/signup");
  await page.fill('input[name="email"]', user.email);
  await page.fill('input[name="password"]', user.password);
  await page.fill('input[name="confirm"]', user.password);
  await page.click('button:has-text("Sign up")');
  await page.waitForURL("**/dashboard");
}

test.describe("ZellaLite core flows", () => {
  test("login, create trade, add journal, filter trades, import csv", async ({ page }) => {
    await signupAndLogin(page);

    await page.goto("/trades/new");
    await page.fill('input[name="symbol"]', "AAPL");
    await page.fill('input[name="opened_at"]', "2024-03-01T09:30");
    await page.fill('input[name="closed_at"]', "2024-03-01T10:00");
    await page.fill('input[name="fees"]', "1.5");
    await page.fill('input[name="executions.0.qty"]', "10");
    await page.fill('input[name="executions.0.price"]', "100");
    await page.click('button:has-text("Add execution")');
    await page.fill('input[name="executions.1.qty"]', "10");
    await page.fill('input[name="executions.1.price"]', "105");
    await page.click('button:has-text("Create trade")');
    await page.waitForURL("**/trades");

    await page.fill('input[name="symbol"]', "AAPL");
    await page.click('button:has-text("Apply filters")');
    await expect(page.locator("table tbody tr")).toHaveCount(1);

    await page.click('a:has-text("View")');
    await page.waitForURL(/\/trades\/[0-9]+/);
    await page.fill("textarea", "Great trade with clean breakout.");
    await page.click('button:has-text("Add note")');
    await expect(page.locator("text=Great trade with clean breakout.")).toBeVisible();

    const csv = "date,time,symbol,side,qty,price,fees,trade_id,notes,strategy\n2024-03-02,09:30,MSFT,buy,5,300,1,1,Entry,Strategy\n2024-03-02,10:00,MSFT,sell,5,310,1,1,Exit,Strategy\n";
    const fileChooserPromise = page.waitForEvent("filechooser");
    await page.goto("/import");
    await page.click('input[type="file"]');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({ name: "import.csv", mimeType: "text/csv", buffer: Buffer.from(csv) });
    await page.click('button:has-text("Preview import")');
    await expect(page.locator("text=Trades processed: 1")).toBeVisible();
  });
});
