// Genere depuis ../qaia-journey/testbooks/US-SITE-001/landing-and-navigation.feature
const { test, expect } = require('@playwright/test');

const PAGES = ['/', '/compare.html', '/walkthrough.html'];

test('@QAIA-US-SITE-001-008 @AC1 @low-confidence the first screen states what goes in and what comes out',
  async ({ page }) => {
    // open: Q1 -- « sans faire defiler » depend de la fenetre. Defaut sur : 1280x720, fixe dans
    // playwright.config.js, et le scenario reste marque @low-confidence tant que personne n'a
    // tranche la question.
    await page.goto('/');
    const foldHeight = page.viewportSize().height;

    const inbound = page.locator('h1');
    await expect(inbound).toContainText(/user story goes in/i);
    const box = await inbound.boundingBox();
    expect(box.y + box.height, "la promesse d'entree doit tenir dans la premiere fenetre")
      .toBeLessThan(foldHeight);

    const outbound = page.getByText(/test book/i).first();
    const outBox = await outbound.boundingBox();
    expect(outBox.y, 'la promesse de sortie doit tenir dans la premiere fenetre')
      .toBeLessThan(foldHeight);
  });

for (const target of PAGES) {
  test(`@QAIA-US-SITE-001-009 @AC2 "${target}" discloses the pre-alpha status`, async ({ page }) => {
    await page.goto(target);
    // La promesse est « le visiteur apprend que le projet est pre-alpha », pas « la page contient
    // telle classe CSS » : on cherche donc le texte visible, ou qu'il soit.
    await expect(page.locator('body')).toContainText(/pre-alpha/i);
  });
}

test('@QAIA-US-SITE-001-010 @AC3 the install block can be copied as it stands', async ({ page }) => {
  await page.goto('/');
  const body = page.locator('body');
  await expect(body).toContainText('/plugin marketplace add https://github.com/QAIA-Project/QAIA');
  await expect(body).toContainText('/plugin install qaia-core@qaia');
  await expect(body).toContainText('/plugin install qaia-playwright@qaia');
});

test('@QAIA-US-SITE-001-011 @AC4 the proof claim points at the artifact behind it', async ({ page }) => {
  await page.goto('/');
  const link = page.locator('a[href*="external-application-2026-08-08"]');
  await expect(link, "l'affirmation de preuve doit pointer le rapport de campagne")
    .toHaveCount(1);
  await expect(link).toHaveAttribute('href', /report\.md$/);
});

test('@QAIA-US-SITE-001-012 @AC5 every in-page navigation anchor has a target', async ({ page }) => {
  await page.goto('/');
  const anchors = await page.locator('a[href^="#"]').evaluateAll((links) =>
    links.map((l) => l.getAttribute('href')).filter((h) => h && h.length > 1)
  );
  expect(anchors.length, 'la page porte des ancres de navigation').toBeGreaterThan(0);
  const missing = [];
  for (const href of anchors) {
    if ((await page.locator(`[id="${href.slice(1)}"]`).count()) === 0) missing.push(href);
  }
  expect(missing, 'chaque ancre doit designer une section existante').toEqual([]);
});

for (const target of PAGES) {
  test(`@QAIA-US-SITE-001-013 @AC7 "${target}" declares its language`, async ({ page }) => {
    await page.goto(target);
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang, 'le document doit declarer une langue').toBeTruthy();
  });
}

test('@QAIA-US-SITE-001-014 @AC7 the three pages carry three different titles', async ({ page }) => {
  const titles = [];
  for (const target of PAGES) {
    await page.goto(target);
    titles.push(await page.title());
  }
  expect(new Set(titles).size, `titres obtenus : ${JSON.stringify(titles)}`).toBe(titles.length);
});
