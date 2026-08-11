// Page object — ecran de connexion Swag Labs. AUCUNE assertion ici : elles vivent dans les specs.
class LoginPage {
  constructor(page) {
    this.page = page;
    this.username = page.getByTestId('username');
    this.password = page.getByTestId('password');
    this.loginButton = page.getByTestId('login-button');
    this.error = page.getByTestId('error');
    this.credentialsPanel = page.getByTestId('login-credentials');
  }

  async goto() {
    await this.page.goto('/');
  }

  /** `null` = champ laisse vide (ce n'est pas la meme chose qu'une chaine vide saisie). */
  async login(username, password) {
    if (username !== null) await this.username.fill(username);
    if (password !== null) await this.password.fill(password);
    await this.loginButton.click();
  }

  errorText() {
    return this.error.textContent();
  }
}

module.exports = { LoginPage };
