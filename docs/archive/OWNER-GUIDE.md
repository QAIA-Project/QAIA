# Guide du propriétaire — actions humaines pour ouvrir QAIA

Ces actions demandent ton identité, ton argent, ton jugement juridique ou tes relations — un agent ne peut pas les faire à ta place. Étapes cliquables + textes prêts à coller. Compte ~20 min hors juridique et recrutement.

## 1. Organisation GitHub + second admin (5 min)
1. https://github.com/organizations/plan → choisir **Free**.
2. Nommer l'org (ex. `qaia-project` — vérifier la dispo, cf. §2).
3. Repo `QAIA-Project/QAIA` → **Settings** → tout en bas **Transfer ownership** → saisir le nom de l'org.
4. Org → **People** → **Invite member** → donner le rôle **Owner** à une personne de confiance (bus factor : ne jamais rester seul admin).
> Après transfert, préviens-moi : je mets à jour les URLs `QAIA-Project/QAIA` codées en dur (marketplace.json, plugin.json, README, skill hello).

## 2. Vérifier le nom (5 min)
- npm : `https://www.npmjs.com/search?q=qaia` · GitHub : barre de recherche · marque : recherche INPI (`data.inpi.fr`) · un produit IA nommé QAIA ? recherche web.
- Si collision, choisir un repli. Décision : **nom non défendu** (D32) — pas de dépôt de marque, mais éviter une vraie confusion.

## 3. Réglages du dépôt (5 min) — Repo → **Settings**
- **General → Features** : cocher **Discussions** (canal pilotes) + **Sponsorships**.
- **Security → Advisories** : activer **Private vulnerability reporting** (c'est le canal de `SECURITY.md`).
- **Branches** → **Add rule** sur `main` : cocher *Require a pull request before merging* + *Require status checks* (choisir le job **CI**) + *Require signed commits* si possible.
- Compte perso → **Settings → Password and authentication** → activer **2FA** (obligatoire pour un mainteneur qui distribue du code exécuté chez autrui).

## 4. GitHub Sponsors (optionnel, 10 min) — quand tu veux
- https://github.com/sponsors → *Join the waitlist / Set up* → il faut un compte bancaire (Stripe). Rien ne presse ; le canal existe pour financer plus tard l'app de démo et le domaine.

## 5. Board Projects (5 min) — onglet **Projects → New project → Board**
Colonnes (copier de `docs/KANBAN.md`) :
`Backlog` · `À challenger` · `Prêt` · `En cours` (limite 2) · `En revue/validation` · `Terminé`
Labels à créer : `P0 P1 P2 P3` · `type:skill type:connecteur type:automatisation type:docs type:infra type:communauté` · `M0…M5` · `dette-de-test good-first-issue needs-discovery stale`
> Je peux générer les issues du backlog à importer si tu veux — dis-le-moi.

## 6. Juridique (irréductible) — AVANT toute communication publique
- Relire contrat de travail + solde de tout compte : non-concurrence (portée/durée/contrepartie), confidentialité, non-sollicitation.
- En cas de doute, avis d'un avocat en droit du travail. La purge du dépôt est faite (D1), mais c'est ton jugement qui débloque la publication.

## 7. Recruter des pilotes (souhaitable, plus un gate bloquant depuis D67)
**Mise à jour 2026-07-25 (D67)** : ce recrutement n'est plus une condition d'entrée en M1 — le développement avance sans l'attendre (`docs/DECISIONS.md`). Rester utile à terme pour une validation conversationnelle réelle (issue #5), mais message ci-dessous à ajuster : ne plus le présenter comme un blocage produit, plutôt comme un appel à du feedback réel une fois que tu veux le faire.

Message prêt à coller ci-dessous (à retoucher). Cible : communautés QA (Ministry of Testing, CFTL, meetups QA FR, LinkedIn). Objectif : des testeurs qui s'engagent à dérouler un cahier réel sous 30 jours.

> 💡 **Pour maximiser les réponses**, pointe les candidats vers [`docs/PILOT-KIT.md`](../PILOT-KIT.md) : un parcours guidé « 15 min » (story prête, install, feedback structuré) qui abaisse l'effort perçu de « 1 h sur ma propre US » à « 15 min ». C'est le levier qui transforme un « peut-être » en « ok je teste ».

---
### Message FR (LinkedIn / MoT)
> **Je cherche 5 testeurs pilotes pour un outil QA open source.**
> Ancien directeur QA, je construis **QAIA** : un outil qui transforme une user story en cahier de test Gherkin priorisé (techniques ISTQB, traçabilité), puis en tests Playwright — le tout dans ta session Claude, sans clé API, sans backend. Open source, généraliste — des workflows métier ordinaires aux domaines exigeants.
> Je cherche **5 testeurs volontaires** pour l'éprouver sur une vraie US à eux et me dire ce qui casse. ~1 h, sous 30 jours. En échange : accès anticipé, ton nom au crédit, et un outil façonné par de vrais testeurs.
> Intéressé·e ? Commente ou DM. 🧪

### Message EN
> **Looking for 5 pilot testers for an open-source QA tool.**
> Former QA director building **QAIA**: turns a user story into a prioritized Gherkin test book (ISTQB techniques, traceability) then Playwright tests — all inside your Claude session, no API key, no backend. Open source, generalist.
> I need **5 volunteer testers** to run it on a real US of their own and tell me what breaks. ~1 h, within 30 days. In return: early access, credit, and a tool shaped by real testers.
> Interested? Comment or DM. 🧪
---

## 8. Vérifier l'installation (5 min, une fois le repo public)
Depuis un autre compte / poste, dans Claude Code :
```
/plugin marketplace add <org>/QAIA
/plugin install qaia-core@qaia
/reload-plugins
/qaia-core:hello
```
`hello` doit répondre et confirmer la version. Rien d'autre à installer.

---
## Ce que je fais, moi, sur simple « go »
- Ouvrir la **PR de merge squash** de la branche vers `main` (purge historique + nom de branche).
- Générer les **issues du backlog** prêtes à importer dans le board.
- Mettre à jour les **URLs** après le transfert vers l'org.
- Continuer les sprints produit (ADR gate D20, skills 0.1.4+, nouveaux gold sets).
