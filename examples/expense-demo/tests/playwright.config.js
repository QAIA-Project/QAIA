const { defineConfig, devices } = require('@playwright/test');
// Reference temporelle de la demo. Les taux de change du SUT sont des fixtures datees
// (2026-07-20..25) : sans horloge figee, les cinq tests qui s'appuient dessus viraient au rouge
// le 2026-10-20 -- et l'un d'eux avec le mauvais message d'erreur, ce qui est pire que rouge.
// Defini ici et nulle part ailleurs ; `make demo` demarre l'application avec la meme valeur.
process.env.DEMO_NOW = process.env.DEMO_NOW || '2026-07-26';

module.exports = defineConfig({
  testDir: '.',
  timeout: 15000,
  // The SUT holds global in-memory state and each test resets it via /api/reset.
  // Parallel workers would stomp each other's resets against the single shared server
  // (same real finding as examples/medibook Sprint 5) -> serialize with one worker.
  workers: 1,
  fullyParallel: false,
  reporter: [['list'], ['json', { outputFile: 'results.json' }]],
  // BASE_URL wiring (external audit finding, 2026-07-26): the CI template already exports a
  // BASE_URL variable but nothing here ever consumed it -- fixed the same way as medibook's.
  use: { baseURL: process.env.BASE_URL || 'http://localhost:4500', trace: 'off', screenshot: 'off' },
  projects: [
    { name: 'e2e-desktop', testMatch: /e2e\..*\.spec\.js/, use: { ...devices['Desktop Chrome'] } },
    { name: 'api', testMatch: /api\..*\.spec\.js/ },
    { name: 'a11y', testMatch: /a11y\..*\.spec\.js/, use: { ...devices['Desktop Chrome'] } },
    // Visual snapshots are platform-specific and must run in the environment that produced
    // the baselines (visual-check guardrail) -- kept as its own project so the other suites can
    // run anywhere without dragging screenshot comparison along.
    // Les references ne sont commitees que pour win32 : le projet ne s'inscrit donc que la
    // ou elles existent. Sans ce filtre, `make test` echouait sur tout clone Linux ou macOS
    // avec des instantanes manquants -- un echec qui ne dit rien du produit (B6). Forcer
    // l'execution ailleurs : VISUAL=1, apres avoir regenere les references localement.
    ...(process.platform === 'win32' || process.env.VISUAL
      ? [{ name: 'visual', testMatch: /visual\..*\.spec\.js/, use: { ...devices['Desktop Chrome'] } }]
      : []),
  ],
});
