/**
 * Scenarios @e2e — Swag Labs (saucedemo.com), US-SD-01 a US-SD-03.
 *
 * SOURCE : `00-BASELINE-sans-skills.md`. Au moment de la generation, `11-saucedemo.feature`
 * N'EXISTAIT PAS dans le dossier de campagne (seul `10-saucedemo-02-observations.txt` etait
 * present). Les identifiants @QAIA-SD-0NN et l'etiquette de niveau @e2e sont donc MIENS,
 * pas ceux d'un cahier : ADR 0008 veut que le niveau soit lu, pas devine, et il n'y avait
 * rien a lire. Chaque titre trace quand meme AC -> test ; l'identifiant devra etre reconcilie
 * avec le cahier Gherkin des qu'il existe.
 *
 * Les tests marques UNCONFIRMED portent un CA que la ligne de base declare explicitement
 * non verifie. Leur rougeur est une REPONSE a une question ouverte, pas une regression.
 */
const { test, expect, PRODUCTS, MSG } = require('../fixtures');

test.describe('US-SD-01 — Se connecter a la boutique', () => {
  test('@QAIA-SD-001 @AC1 @e2e Un couple valide ouvre la page catalogue', async ({ loginPage, inventoryPage, page }) => {
    await loginPage.goto();
    await loginPage.login('standard_user', 'secret_sauce');

    await expect(page).toHaveURL(/\/inventory\.html$/);
    await expect(inventoryPage.title).toHaveText('Products');
    await expect(inventoryPage.items).toHaveCount(6);
  });

  test('@QAIA-SD-002 @AC2 @e2e Un identifiant absent est refuse par un message qui nomme le champ', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.login(null, 'secret_sauce');

    await expect(loginPage.error).toHaveText(MSG.usernameRequired);
    // le CA exige un refus AVANT toute autre verification : on reste sur la page de connexion
    await expect(page).not.toHaveURL(/\/inventory\.html/);
  });

  test('@QAIA-SD-003 @AC3 @e2e Un mot de passe absent est refuse par un message qui nomme le champ', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.login('standard_user', null);

    await expect(loginPage.error).toHaveText(MSG.passwordRequired);
    await expect(page).not.toHaveURL(/\/inventory\.html/);
  });

  test('@QAIA-SD-004 @AC4 @e2e Un couple inconnu est refuse sans reveler lequel des deux est faux', async ({ loginPage, page }) => {
    // Le CA porte sur une NON-DISTINCTION : un seul cas ne peut pas la prouver. Le test
    // exerce donc les deux cotes et asserte leur EGALITE (self-review D5/D7 : une clause de
    // non-divulgation demande une assertion de similitude entre deux cas, pas une assertion
    // isolee sur un seul).
    await loginPage.goto();
    await loginPage.login('no_such_user_at_all', 'secret_sauce');
    const unknownAccountMessage = await loginPage.errorText();

    await loginPage.goto();
    await loginPage.login('standard_user', 'definitely_wrong');
    const wrongPasswordMessage = await loginPage.errorText();

    expect(unknownAccountMessage).toBe(wrongPasswordMessage);
    expect(unknownAccountMessage).toBe(MSG.noMatch);
    await expect(page).not.toHaveURL(/\/inventory\.html/);
  });

  test('@QAIA-SD-005 @AC5 @e2e Un compte verrouille est refuse par un message de verrouillage, pas de mauvais identifiants', async ({ loginPage, page }) => {
    await loginPage.goto();
    await loginPage.login('locked_out_user', 'secret_sauce');

    await expect(loginPage.error).toHaveText(MSG.lockedOut);
    // la seconde moitie du CA : ce message n'est PAS le message generique de couple inconnu
    expect(await loginPage.errorText()).not.toBe(MSG.noMatch);
    await expect(page).not.toHaveURL(/\/inventory\.html/);
  });

  test('@QAIA-SD-006 @AC6 @e2e @unconfirmed Apres un refus, l identifiant reste affiche et le mot de passe est vide', async ({ loginPage }) => {
    // UNCONFIRMED — la ligne de base ecrit noir sur blanc : "AC6 est une supposition de ma
    // part : je ne l'ai pas verifiee". L'assertion suit donc le CA, pas l'application.
    // Un ECHEC ICI EST UNE REPONSE A LA QUESTION OUVERTE, pas une regression produit :
    // ne pas "corriger" ce test en alignant l'attendu sur ce que l'application fait
    // (self-review D5/D6) — c'est au produit d'arbitrer.
    await loginPage.goto();
    await loginPage.login('standard_user', 'definitely_wrong');

    await expect(loginPage.error).toHaveText(MSG.noMatch);
    await expect(loginPage.username).toHaveValue('standard_user');
    await expect(loginPage.password).toHaveValue('');
  });

  test('@QAIA-SD-007 @AC7 @e2e La page catalogue n est pas accessible sans etre connecte', async ({ page, inventoryPage }) => {
    // aucun amorcage de session : le contexte est vierge
    const response = await page.goto('/inventory.html');

    await expect(inventoryPage.items).toHaveCount(0);
    // message releve au precheck du 2026-08-11 (provenance : observation, pas hypothese)
    await expect(page.getByTestId('error')).toContainText("You can only access '/inventory.html' when you are logged in.");
    expect(response.status()).not.toBe(200);
  });
});

test.describe('US-SD-02 — Composer un panier', () => {
  test('@QAIA-SD-008 @AC1 @e2e Ajouter un article incremente la pastille du panier de 1', async ({ seed, inventoryPage }) => {
    await seed({ user: 'standard_user' });
    await inventoryPage.goto();
    await expect(inventoryPage.cartBadge).toHaveCount(0);

    await inventoryPage.addToCartButton(PRODUCTS.backpack.slug).click();

    await expect(inventoryPage.cartBadge).toHaveText('1');
  });

  test('@QAIA-SD-009 @AC2 @e2e Le bouton d un article ajoute devient Remove', async ({ seed, inventoryPage }) => {
    await seed({ user: 'standard_user' });
    await inventoryPage.goto();

    await inventoryPage.addToCartButton(PRODUCTS.backpack.slug).click();

    await expect(inventoryPage.removeButton(PRODUCTS.backpack.slug)).toBeVisible();
    await expect(inventoryPage.removeButton(PRODUCTS.backpack.slug)).toHaveText('Remove');
    await expect(inventoryPage.addToCartButton(PRODUCTS.backpack.slug)).toHaveCount(0);
  });

  test('@QAIA-SD-010 @AC3 @e2e Retirer un article decremente la pastille et a zero elle disparait', async ({ seed, inventoryPage }) => {
    await seed({ user: 'standard_user', cart: [PRODUCTS.backpack, PRODUCTS.onesie] });
    await inventoryPage.goto();
    await expect(inventoryPage.cartBadge).toHaveText('2');

    await inventoryPage.removeButton(PRODUCTS.onesie.slug).click();
    await expect(inventoryPage.cartBadge).toHaveText('1');

    await inventoryPage.removeButton(PRODUCTS.backpack.slug).click();
    await expect(inventoryPage.cartBadge).toHaveCount(0);
  });

  test('@QAIA-SD-011 @AC4 @e2e Le panier contient exactement les articles ajoutes, libelle et prix identiques au catalogue', async ({ seed, inventoryPage, cartPage }) => {
    const chosen = [PRODUCTS.backpack, PRODUCTS.onesie];
    await seed({ user: 'standard_user', cart: chosen });

    // les prix du catalogue sont relus SUR L'ECRAN, pas seulement compares a une constante :
    // le CA parle d'identite entre deux ecrans, pas de conformite a une valeur attendue.
    await inventoryPage.goto();
    const cataloguePrices = {};
    for (const p of chosen) cataloguePrices[p.name] = await inventoryPage.priceOf(p.name).textContent();

    await cartPage.goto();

    await expect(cartPage.items).toHaveCount(chosen.length);
    await expect(cartPage.names).toHaveText(chosen.map((p) => p.name));
    for (const p of chosen) {
      await expect(cartPage.priceOf(p.name)).toHaveText(cataloguePrices[p.name]);
      await expect(cartPage.priceOf(p.name)).toHaveText(`$${p.price.toFixed(2)}`);
    }
    // "exactement" : aucun article non choisi
    await expect(cartPage.row(PRODUCTS.fleeceJacket.name)).toHaveCount(0);
  });

  test('@QAIA-SD-012 @AC5 @e2e Le contenu du panier survit a un aller-retour vers une fiche article', async ({ seed, inventoryPage, page }) => {
    await seed({ user: 'standard_user', cart: [PRODUCTS.backpack] });
    await inventoryPage.goto();
    await expect(inventoryPage.cartBadge).toHaveText('1');

    await inventoryPage.titleLink(PRODUCTS.bikeLight.id).click();
    await expect(page).toHaveURL(/inventory-item\.html\?id=0/);
    await page.getByTestId('back-to-products').click();
    await expect(page).toHaveURL(/\/inventory\.html$/);

    await expect(inventoryPage.cartBadge).toHaveText('1');
    expect(JSON.parse(await inventoryPage.readCartStorage())).toEqual([PRODUCTS.backpack.id]);
  });

  test('@QAIA-SD-013 @AC6 @e2e Le tri du catalogue ne modifie pas le contenu du panier', async ({ seed, inventoryPage }) => {
    const chosen = [PRODUCTS.backpack, PRODUCTS.onesie];
    await seed({ user: 'standard_user', cart: chosen });
    await inventoryPage.goto();
    await expect(inventoryPage.cartBadge).toHaveText('2');

    await inventoryPage.sortBy('hilo');
    // le tri a bien eu lieu : sans ce controle, le CA serait verifie contre un non-evenement
    await expect(inventoryPage.prices.first()).toHaveText(`$${PRODUCTS.fleeceJacket.price.toFixed(2)}`);

    await expect(inventoryPage.cartBadge).toHaveText('2');
    expect(JSON.parse(await inventoryPage.readCartStorage()).sort()).toEqual(chosen.map((p) => p.id).sort());
  });
});

test.describe('US-SD-03 — Passer commande', () => {
  const ADDRESS = { first: 'Ada', last: 'Lovelace', zip: '05000' };

  for (const [field, filled, message] of [
    ['firstName', { last: ADDRESS.last, zip: ADDRESS.zip }, MSG.firstNameRequired],
    ['lastName', { first: ADDRESS.first, zip: ADDRESS.zip }, MSG.lastNameRequired],
    ['postalCode', { first: ADDRESS.first, last: ADDRESS.last }, MSG.postalCodeRequired],
  ]) {
    const id = { firstName: '014', lastName: '015', postalCode: '016' }[field];
    test(`@QAIA-SD-${id} @AC1 @AC2 @e2e Le champ ${field} est obligatoire et son absence est nommee`, async ({ seed, checkoutPage, page }) => {
      await seed({ user: 'standard_user', cart: [PRODUCTS.backpack] });
      await checkoutPage.gotoStepOne();

      await checkoutPage.fillAddress(filled);
      await checkoutPage.continueButton.click();

      await expect(checkoutPage.error).toHaveText(message);
      await expect(page).toHaveURL(/checkout-step-one\.html$/);
    });
  }

  test('@QAIA-SD-017 @AC3 @e2e Le recapitulatif affiche sous-total, taxe et total', async ({ seed, checkoutPage, page }) => {
    await seed({ user: 'standard_user', cart: [PRODUCTS.backpack] });
    await checkoutPage.gotoStepOne();
    await checkoutPage.fillAddress(ADDRESS);
    await checkoutPage.continueButton.click();

    await expect(page).toHaveURL(/checkout-step-two\.html$/);
    await expect(checkoutPage.subtotalLabel).toHaveText(`Item total: $${PRODUCTS.backpack.price.toFixed(2)}`);
    await expect(checkoutPage.taxLabel).toContainText('Tax: $');
    await expect(checkoutPage.totalLabel).toContainText('Total: $');
    expect(await checkoutPage.tax()).toBeGreaterThan(0);
    expect(await checkoutPage.total()).toBeGreaterThan(await checkoutPage.subtotal());
  });

  test('@QAIA-SD-018 @AC4 @e2e Le total est la somme du sous-total et de la taxe', async ({ seed, checkoutPage }) => {
    await seed({ user: 'standard_user', cart: [PRODUCTS.backpack, PRODUCTS.fleeceJacket, PRODUCTS.onesie] });
    await checkoutPage.gotoStepOne();
    await checkoutPage.fillAddress(ADDRESS);
    await checkoutPage.continueButton.click();

    const [subtotal, tax, total] = [await checkoutPage.subtotal(), await checkoutPage.tax(), await checkoutPage.total()];
    // oracle calcule sur l'etat lu a l'ecran, aucune valeur attendue codee en dur
    expect(Number((subtotal + tax).toFixed(2))).toBe(total);
    // et le sous-total est bien celui du panier pose, sinon l'egalite ci-dessus serait vraie
    // sur n'importe quel triplet coherent (self-review D1 : eviter l'auto-coherence)
    const expectedSubtotal = PRODUCTS.backpack.price + PRODUCTS.fleeceJacket.price + PRODUCTS.onesie.price;
    expect(subtotal).toBe(Number(expectedSubtotal.toFixed(2)));
  });

  test('@QAIA-SD-019 @AC5 @e2e @unconfirmed La taxe vaut 8 % du sous-total arrondi au centime', async ({ seed, checkoutPage }) => {
    // UNCONFIRMED — la ligne de base tire "8 %" d'UNE SEULE observation ($29.99 -> $2.40) et
    // le dit : "C'est une hypothese, pas un constat". Le test l'eprouve sur DEUX compositions
    // de panier differentes ; c'est ce que le CA reclame et ce qu'une seule mesure ne peut
    // pas donner. Un echec ici invalide la regle deduite, il n'accuse pas l'application.
    for (const cart of [[PRODUCTS.backpack], [PRODUCTS.fleeceJacket, PRODUCTS.bikeLight, PRODUCTS.onesie]]) {
      await seed({ user: 'standard_user', cart });
      await checkoutPage.gotoStepOne();
      await checkoutPage.fillAddress(ADDRESS);
      await checkoutPage.continueButton.click();

      const subtotal = await checkoutPage.subtotal();
      const tax = await checkoutPage.tax();
      expect(tax).toBe(Number((subtotal * 0.08).toFixed(2)));
    }
  });

  test('@QAIA-SD-020 @AC6 @e2e Confirmer la commande affiche une confirmation et vide le panier', async ({ seed, checkoutPage, cartPage, page }) => {
    await seed({ user: 'standard_user', cart: [PRODUCTS.backpack] });
    await checkoutPage.gotoStepOne();
    await checkoutPage.fillAddress(ADDRESS);
    await checkoutPage.continueButton.click();
    await checkoutPage.finishButton.click();

    await expect(page).toHaveURL(/checkout-complete\.html$/);
    await expect(checkoutPage.completeHeader).toHaveText('Thank you for your order!');
    // "et vide le panier" : la seconde clause du Then a sa propre assertion (self-review D9)
    await expect(checkoutPage.cartBadge).toHaveCount(0);
    await cartPage.goto();
    await expect(cartPage.items).toHaveCount(0);
  });

  test('@QAIA-SD-021 @AC7 @e2e @unconfirmed Un panier vide ne permet pas d atteindre la confirmation', async ({ seed, checkoutPage, page }) => {
    // UNCONFIRMED — la ligne de base ecrit : "AC7 est egalement non verifie : je n'ai pas
    // essaye." L'assertion suit le CA. Un echec ici est la reponse a cette question ouverte.
    await seed({ user: 'standard_user' });
    await checkoutPage.gotoStepOne();
    await checkoutPage.fillAddress(ADDRESS);
    await checkoutPage.continueButton.click();
    await checkoutPage.finishButton.click().catch(() => {});

    await expect(page).not.toHaveURL(/checkout-complete\.html$/);
    await expect(checkoutPage.completeHeader).toHaveCount(0);
  });
});
