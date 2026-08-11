// Généré par qaia-playwright:automate pour le cahier BOOK-API — 100 % @api (ADR 0008).
// Un seul projet, `api`, SANS `browserName` ni descripteur d'appareil : ces tests passent par
// APIRequestContext, aucun moteur de rendu n'entre dans leur résultat. C'est le découpage que
// le niveau du cahier impose, pas une préférence — et il se voit ici : la suite ne lance aucun
// navigateur et n'en installe aucun.
const { defineConfig } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:4600';

module.exports = defineConfig({
  testDir: '.',
  // 0 nouvelle tentative : masquer une instabilité effacerait le signal que flaky-detect existe
  // pour montrer. Politique du dépôt, pas un réglage local.
  retries: 0,
  // Un seul worker : les tests partagent un serveur avec un état en mémoire, que chacun remet
  // à zéro par /test/reset. Paralléliser les ferait se voler leur état.
  workers: 1,
  reporter: [['list'], ['junit', { outputFile: 'junit.xml' }], ['json', { outputFile: 'results.json' }]],
  use: { baseURL: BASE_URL },
  projects: [{ name: 'api' }],
  webServer: {
    command: 'node ../app/server.js',
    url: `${BASE_URL}/health`,
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
  },
});
