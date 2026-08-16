const { test, expect } = require('@playwright/test');

const assets = Array.from({ length: 10 }, (_, index) => `ENG-${String(index + 1).padStart(3, '0')}`);

function intersects(a, b, padding = 0) {
  return !(
    a.x + a.width + padding <= b.x ||
    b.x + b.width + padding <= a.x ||
    a.y + a.height + padding <= b.y ||
    b.y + b.height + padding <= a.y
  );
}

async function box(locator) {
  const result = await locator.boundingBox();
  expect(result).not.toBeNull();
  return result;
}

for (const assetId of assets) {
  test(`${assetId} diagram has clear geometry and part-level stats`, async ({ page }) => {
    await page.goto(`/?asset=${assetId}#asset`);
    await expect(page.locator('.twin-asset')).toBeVisible();
    await expect(page.locator('#assetTwinName')).not.toContainText('ENG-');

    const stage = await box(page.locator('#engineStage'));
    const ring = await box(page.locator('.twin-status-ring'));
    const icon = await box(page.locator('.twin-asset .equipment-icon'));
    const tag = await box(page.locator('.twin-tag'));
    const type = await box(page.locator('.twin-type'));
    const source = await box(page.locator('.twin-source'));
    const telemetry = await box(page.locator('.telemetry-cards'));

    expect(ring.y + ring.height + 8).toBeLessThanOrEqual(tag.y);
    expect(tag.y + tag.height + 4).toBeLessThanOrEqual(type.y);
    expect(type.y + type.height + 4).toBeLessThanOrEqual(source.y);
    expect(source.y + source.height).toBeLessThanOrEqual(telemetry.y - 6);
    expect(icon.x).toBeGreaterThanOrEqual(ring.x);
    expect(icon.y).toBeGreaterThanOrEqual(ring.y);
    expect(icon.x + icon.width).toBeLessThanOrEqual(ring.x + ring.width);
    expect(icon.y + icon.height).toBeLessThanOrEqual(ring.y + ring.height);
    expect(telemetry.x).toBeGreaterThanOrEqual(stage.x);
    expect(telemetry.x + telemetry.width).toBeLessThanOrEqual(stage.x + stage.width);

    const callouts = page.locator('.sensor-callout');
    await expect(callouts).toHaveCount(4);
    for (let index = 0; index < 4; index += 1) {
      const callout = callouts.nth(index);
      const labelBox = await box(callout.locator('text'));
      const lineBox = await box(callout.locator('line'));
      expect(intersects(labelBox, lineBox, 2)).toBe(false);
      expect(intersects(labelBox, ring, 4)).toBe(false);
      expect(intersects(labelBox, tag, 4)).toBe(false);
      expect(intersects(labelBox, type, 4)).toBe(false);
      expect(intersects(labelBox, source, 4)).toBe(false);
      expect(labelBox.x).toBeGreaterThanOrEqual(stage.x);
      expect(labelBox.x + labelBox.width).toBeLessThanOrEqual(stage.x + stage.width);

      await callout.locator('.sensor-hit').hover();
      await expect(page.locator('#assetTooltip')).toBeVisible();
      await expect(page.locator('#assetTooltip .sensor-tooltip')).toBeVisible();
      await expect(page.locator('#assetTooltip .sensor-reading strong')).not.toHaveText('NaN');
      await page.mouse.move(2, 2);
    }

    await page.locator('.twin-hit').hover();
    await expect(page.locator('#assetTooltip')).toBeVisible();
    await expect(page.locator('#assetTooltip .tooltip-grid')).toBeVisible();
    await expect(page.locator('#assetTooltip')).toContainText('RUL P50');
  });
}

test('every overview part exposes stats and keeps labels clear', async ({ page }) => {
  await page.goto('/#overview');
  const parts = page.locator('.machine-group');
  await expect(parts).toHaveCount(8);

  for (let index = 0; index < 8; index += 1) {
    const part = parts.nth(index);
    const ring = await box(part.locator('.machine-ring'));
    const label = await box(part.locator('.machine-label'));
    const type = await box(part.locator('.machine-type'));
    const meta = await box(part.locator('.machine-meta'));

    expect(ring.y + ring.height + 5).toBeLessThanOrEqual(label.y);
    expect(label.y + label.height + 1).toBeLessThanOrEqual(type.y);
    expect(type.y + type.height + 1).toBeLessThanOrEqual(meta.y);

    await part.locator('.machine-hit').hover();
    await expect(page.locator('#assetTooltip .tooltip-grid')).toBeVisible();
    await expect(page.locator('#assetTooltip')).toContainText('Health');
    await expect(page.locator('#assetTooltip')).toContainText('RUL P50');
    await page.mouse.move(2, 2);
  }
});
