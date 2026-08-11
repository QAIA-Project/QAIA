// Genere par qaia-playwright:automate pour le cahier US-SITE-001.
// Deux projets, parce que le cahier porte deux niveaux (ADR 0008) : `api` sans moteur de
// navigateur pour les promesses observables en HTTP, `e2e-desktop` pour celles qui n'existent
// qu'a l'ecran. Le decoupage est LU dans les etiquettes du cahier, il n'est pas devine ici.
const { defineConfig, devices } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:4700';

module.exports = defineConfig({
  testDir: '.',
  retries: 0,
  reporter: [['list'], ['junit', { outputFile: 'junit.xml' }], ['json', { outputFile: 'results.json' }]],
  use: { baseURL: BASE_URL },
  projects: [
    { name: 'api', testMatch: /api\..*\.spec\.js/ },
    {
      name: 'e2e-desktop',
      testMatch: /e2e\..*\.spec\.js/,
      // 1280x720 : le defaut sur applique a la question ouverte Q1 (« sans faire defiler » n'a
      // pas de definition). Le scenario qui en depend est marque @low-confidence dans le cahier.
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 720 } },
    },
  ],
  webServer: {
    command: 'node serve.js',
    url: `${BASE_URL}/robots.txt`,
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
  },
});
