// Page object — catalogue Swag Labs. Aucune assertion ici.
class InventoryPage {
  constructor(page) {
    this.page = page;
    this.title = page.getByTestId('title');
    this.items = page.getByTestId('inventory-item');
    this.names = page.getByTestId('inventory-item-name');
    this.prices = page.getByTestId('inventory-item-price');
    this.sortSelect = page.getByTestId('product-sort-container');
    this.cartLink = page.getByTestId('shopping-cart-link');
    this.cartBadge = page.getByTestId('shopping-cart-badge');
    this.burger = page.getByTestId('open-menu');
    this.resetLink = page.getByTestId('reset-sidebar-link');
    this.logoutLink = page.getByTestId('logout-sidebar-link');
  }

  async goto() {
    await this.page.goto('/inventory.html');
  }

  addToCartButton(slug) {
    return this.page.getByTestId(`add-to-cart-${slug}`);
  }

  removeButton(slug) {
    return this.page.getByTestId(`remove-${slug}`);
  }

  /** Lien titre de l'article : l'identifiant est celui porte par le DOM (item-<id>-title-link). */
  titleLink(id) {
    return this.page.getByTestId(`item-${id}-title-link`);
  }

  row(name) {
    return this.items.filter({ has: this.page.getByTestId('inventory-item-name').getByText(name, { exact: true }) });
  }

  priceOf(name) {
    return this.row(name).getByTestId('inventory-item-price');
  }

  async sortBy(value) {
    await this.sortSelect.selectOption(value);
  }

  /** Etat du panier lu au format applicatif (localStorage `cart-contents`). */
  readCartStorage() {
    return this.page.evaluate(() => window.localStorage.getItem('cart-contents'));
  }
}

module.exports = { InventoryPage };
