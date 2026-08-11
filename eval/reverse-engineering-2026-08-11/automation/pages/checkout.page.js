// Page object — tunnel de commande Swag Labs (etapes 1, 2 et confirmation). Aucune assertion ici.
class CheckoutPage {
  constructor(page) {
    this.page = page;
    // etape 1
    this.firstName = page.getByTestId('firstName');
    this.lastName = page.getByTestId('lastName');
    this.postalCode = page.getByTestId('postalCode');
    this.continueButton = page.getByTestId('continue');
    this.cancelButton = page.getByTestId('cancel');
    this.error = page.getByTestId('error');
    // etape 2
    this.subtotalLabel = page.getByTestId('subtotal-label');
    this.taxLabel = page.getByTestId('tax-label');
    this.totalLabel = page.getByTestId('total-label');
    this.finishButton = page.getByTestId('finish');
    this.summaryItems = page.getByTestId('inventory-item');
    // confirmation
    this.completeHeader = page.getByTestId('complete-header');
    this.completeText = page.getByTestId('complete-text');
    this.cartBadge = page.getByTestId('shopping-cart-badge');
  }

  async gotoStepOne() {
    await this.page.goto('/checkout-step-one.html');
  }

  /** `null` = champ laisse vide. */
  async fillAddress({ first = null, last = null, zip = null } = {}) {
    if (first !== null) await this.firstName.fill(first);
    if (last !== null) await this.lastName.fill(last);
    if (zip !== null) await this.postalCode.fill(zip);
  }

  /** "Item total: $29.99" -> 29.99 ; renvoie NaN si l'etiquette ne porte aucun montant. */
  static amount(label) {
    const m = /\$(-?\d+(?:\.\d+)?)/.exec(label || '');
    return m ? Number(m[1]) : NaN;
  }

  async subtotal() { return CheckoutPage.amount(await this.subtotalLabel.textContent()); }
  async tax() { return CheckoutPage.amount(await this.taxLabel.textContent()); }
  async total() { return CheckoutPage.amount(await this.totalLabel.textContent()); }
}

module.exports = { CheckoutPage };
