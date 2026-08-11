// Page object — panier Swag Labs. Aucune assertion ici.
class CartPage {
  constructor(page) {
    this.page = page;
    this.title = page.getByTestId('title');
    this.items = page.getByTestId('inventory-item');
    this.names = page.getByTestId('inventory-item-name');
    this.prices = page.getByTestId('inventory-item-price');
    this.quantities = page.getByTestId('item-quantity');
    this.checkoutButton = page.getByTestId('checkout');
    this.continueShoppingButton = page.getByTestId('continue-shopping');
    this.cartBadge = page.getByTestId('shopping-cart-badge');
  }

  async goto() {
    await this.page.goto('/cart.html');
  }

  removeButton(slug) {
    return this.page.getByTestId(`remove-${slug}`);
  }

  row(name) {
    return this.items.filter({ has: this.page.getByTestId('inventory-item-name').getByText(name, { exact: true }) });
  }

  priceOf(name) {
    return this.row(name).getByTestId('inventory-item-price');
  }
}

module.exports = { CartPage };
