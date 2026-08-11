// POM-as-fixtures + amorçage declaratif de l'etat, pour les scenarios @e2e (saucedemo.com).
const base = require('@playwright/test');
const { LoginPage } = require('./pages/login.page');
const { InventoryPage } = require('./pages/inventory.page');
const { CartPage } = require('./pages/cart.page');
const { CheckoutPage } = require('./pages/checkout.page');

/**
 * Catalogue de reference.
 * PROVENANCE : releve par exploration du catalogue le 2026-08-11 (precheck de testabilite).
 * `id` est l'identifiant porte par le DOM (`item-<id>-title-link`), `slug` celui des boutons
 * (`add-to-cart-<slug>`), `price` le prix affiche au catalogue.
 * Aucune de ces valeurs n'est inventee : chacune est un constat, pas une hypothese.
 */
const PRODUCTS = {
  backpack: { id: 4, slug: 'sauce-labs-backpack', name: 'Sauce Labs Backpack', price: 29.99 },
  bikeLight: { id: 0, slug: 'sauce-labs-bike-light', name: 'Sauce Labs Bike Light', price: 9.99 },
  boltTShirt: { id: 1, slug: 'sauce-labs-bolt-t-shirt', name: 'Sauce Labs Bolt T-Shirt', price: 15.99 },
  fleeceJacket: { id: 5, slug: 'sauce-labs-fleece-jacket', name: 'Sauce Labs Fleece Jacket', price: 49.99 },
  onesie: { id: 2, slug: 'sauce-labs-onesie', name: 'Sauce Labs Onesie', price: 7.99 },
};

/**
 * Messages d'erreur.
 * PROVENANCE : releves au caractere pres dans `00-BASELINE-sans-skills.md` (cible 1) et
 * reconfirmes par le precheck du 2026-08-11.
 */
const MSG = {
  usernameRequired: 'Epic sadface: Username is required',
  passwordRequired: 'Epic sadface: Password is required',
  noMatch: 'Epic sadface: Username and password do not match any user in this service',
  lockedOut: 'Epic sadface: Sorry, this user has been locked out.',
  firstNameRequired: 'Error: First Name is required',
  lastNameRequired: 'Error: Last Name is required',
  postalCodeRequired: 'Error: Postal Code is required',
};

const SD_HOST = new URL(process.env.SD_BASE_URL || 'https://www.saucedemo.com').hostname;

const test = base.test.extend({
  loginPage: async ({ page }, use) => { await use(new LoginPage(page)); },
  inventoryPage: async ({ page }, use) => { await use(new InventoryPage(page)); },
  cartPage: async ({ page }, use) => { await use(new CartPage(page)); },
  checkoutPage: async ({ page }, use) => { await use(new CheckoutPage(page)); },

  /**
   * Precondition ATOMIQUE et DECLARATIVE — pas d'enchainement d'interface.
   * Le precheck de testabilite a etabli que l'etat applicatif tient dans deux endroits
   * observables et inscriptibles :
   *   - la session : cookie `session-username` (non httpOnly) ;
   *   - le panier   : cle localStorage `cart-contents` (tableau des `id` produits).
   * Poser l'etat ici evite de traverser la connexion et le catalogue pour tester le tunnel.
   */
  seed: async ({ context }, use) => {
    await use(async ({ user = 'standard_user', cart = null } = {}) => {
      if (user) {
        await context.addCookies([{ name: 'session-username', value: user, domain: SD_HOST, path: '/' }]);
      }
      if (cart) {
        // Le script s'execute a CHAQUE navigation. Sans le garde-fou ci-dessous il rejouerait
        // l'amorcage apres chaque changement de page et RECREERAIT le panier que l'application
        // vient de vider — @QAIA-SD-020 est passe au rouge pour cette raison, et @QAIA-SD-012 /
        // @QAIA-SD-013 etaient verts sans rien prouver. L'amorcage ne doit avoir lieu qu'une
        // fois, a l'ouverture du contexte : ensuite, l'etat appartient a l'application.
        await context.addInitScript(
          ([value, marker]) => {
            if (window.sessionStorage.getItem(marker)) return;
            window.sessionStorage.setItem(marker, '1');
            window.localStorage.setItem('cart-contents', value);
          },
          [JSON.stringify(cart.map((p) => p.id)), 'qaia-cart-seeded'],
        );
      }
    });
  },
});

module.exports = { test, expect: base.expect, PRODUCTS, MSG };
