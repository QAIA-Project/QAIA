// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Suite generee par qaia-playwright:automate — campagne reverse-engineering 2026-08-11.
 *
 * Deux projets, decoupes par l'etiquette de NIVEAU portee par le scenario (ADR 0008) :
 *   - `e2e-desktop` : les scenarios @e2e (saucedemo.com) — un seul moteur, aucune matrice
 *     de navigateurs : aucun des CA couverts ici ne depend de la mise en page, des controles
 *     natifs, de l'ordre de focus ni de la politique de stockage.
 *   - `api`         : les scenarios @api (restful-booker) — AUCUN `browserName`, AUCUN
 *     descripteur d'appareil. 55 des 76 cas sont des requetes HTTP : les multiplier par un
 *     moteur de rendu ne peut pas changer leur resultat.
 */
module.exports = defineConfig({
  testDir: './specs',

  // retries: 0, ecrit ici et pas renvoye a un document.
  // Masquer l'instabilite derriere des reprises automatiques efface exactement le signal
  // que `flaky-detect` existe pour faire remonter. On choisit de voir les echecs.
  retries: 0,

  // workers: 1 — restful-booker est un SUT public et partage, et la consigne de campagne
  // interdit toute execution parallele massive. Un seul worker borne aussi l'empreinte
  // reseau (compteur ecrit dans request-count.json).
  workers: 1,

  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  timeout: 45_000,
  expect: { timeout: 10_000 },

  reporter: [
    ['list'],
    ['junit', { outputFile: 'junit.xml' }],
    ['json', { outputFile: 'results.json' }],
    ['html', { open: 'never', outputFolder: 'playwright-report' }],
  ],

  projects: [
    {
      name: 'e2e-desktop',
      testMatch: /e2e\..*\.spec\.js/,
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.SD_BASE_URL || 'https://www.saucedemo.com',
        // saucedemo n'expose pas data-testid mais data-test : on aligne getByTestId dessus
        // plutot que de retomber sur des selecteurs CSS positionnels.
        testIdAttribute: 'data-test',
        trace: 'retain-on-failure',
        screenshot: 'only-on-failure',
      },
    },
    {
      name: 'api',
      testMatch: /api\..*\.spec\.js/,
      // Pas de `browserName`, pas de `...devices[...]` : ce projet ne lance aucun navigateur.
      use: {
        baseURL: process.env.RB_BASE_URL || 'https://restful-booker.herokuapp.com',
      },
    },
  ],
});
