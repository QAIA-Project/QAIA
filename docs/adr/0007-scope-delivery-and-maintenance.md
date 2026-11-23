# ADR 0007 — Le périmètre est Delivery et Maintenance, et on l'assume

- Statut : **Accepté**
- Date : 2026-08-08
- Décidé par : le fondateur, après une revue d'architecture menée sur le dépôt
- **Remplace [ADR 0005](0005-scope-discovery-and-run.md)**
- *État au 2026-11-23 : la borne reste vraie, mais le produit couvre bien moins que ce périmètre.
  Les skills de Maintenance (`locator-repair`, `flaky-detect`, `confirm-fix`, `impact-select`,
  `run-report`) ont été supprimées le 2026-10-26 par la
  [refonte](../superpowers/specs/2026-08-24-qaia-refonte-design.md) : de l'outillage de CI qui
  appartient à qui possède le lanceur. Il reste 4 skills ; la Maintenance n'est plus servie que par
  `probe` (rapport d'anomalie, rejeu de trafic capturé).*

## Contexte, et le fait qu'il faut écrire en premier

**Cette décision annule une décision prise le même jour, quelques heures plus tôt.**

[ADR 0005](0005-scope-discovery-and-run.md) actait l'inverse — viser Discovery et Run — au motif que
le différenciateur revendiqué était la couverture du cycle. Quatre issues avaient été ouvertes.

Entre les deux, une revue d'architecture a été menée **sur le dépôt**, avec obligation de preuve.
Deux de ses résultats retournent le raisonnement d'ADR 0005 :

**1. La capacité existante n'est pas prouvée.** L'hypothèse « le problème est l'adoption plutôt que
la capacité » est **infirmée** : cinq juges à contexte vide sur cinq suites générées, aucune ne
franchit la porte (3/12, 4/12, 2/12, 5/12 — D144) ; le cahier vitrine assérait 17 codes HTTP absents
de l'exigence, trouvé par un concurrent et non par les gardes internes (#83) ; le prompt direct
égale ou dépasse QAIA sur le rappel des ambiguïtés pour 2,9× moins de jetons. **Élargir ajouterait
de la surface non prouvée à de la surface non prouvée.**

**2. Le motif d'ADR 0005 ne tient plus.** Un différenciateur qu'on ne peut pas démontrer n'en est
pas un — et la même revue a montré que **les chiffres qui le soutenaient étaient faux dans des
fichiers livrés** : `26 tests` annoncés `31` puis `24`, dont une fois dans une `SKILL.md` empaquetée.

## Décision

**QAIA couvre le test dans Delivery et Maintenance. Point.**

**1. Discovery et Run sortent du périmètre.** Pas de dérivation d'exigences non-fonctionnelles en
amont, ni monitoring synthétique, ni chaos, ni incident-vers-test. `traffic-replay` reste ce qu'il
est : un rejeu de trafic fourni par l'utilisateur, pas une porte vers le Run.

**2. L'automatisation reste strictement Playwright.** Ni Cypress, ni Selenium, ni pytest, ni JUnit.
Un concurrent direct en sort six ; c'est un écart en sa faveur, mesuré et assumé. Multiplier les
cibles multiplie la surface à prouver, et aucune n'est prouvée auprès d'un utilisateur.

**3. Pas de FinOps.** Le budget en jetons reste mesuré par skill ; rien ne le pilote.

## Ce que cette décision ne tranche PAS

**La portabilité reste ouverte.** [ADR 0006](0006-multi-agent-portability.md) tient : les skills
doivent tourner dans l'agent que l'utilisateur possède déjà.

Une première rédaction de cette ADR fermait aussi le levier — « on assume un agent capable », donc
pas de gabarit contraint ni de valider-et-redemander. **Retiré**, sur une preuve trouvée après :
`mcp-bridge/` existe déjà dans le dépôt, avec `src/`, des tests dans `test/`, et un README qui
l'annonce explicitement pour **Cursor et GitHub Copilot**. Aucun job de CI ne l'exécute.

Trancher le levier de portabilité avant d'avoir fait tourner ces tests reviendrait à décider sans
mesurer — ce que cette même revue reproche par ailleurs. La décision attend ; #88 reste ouverte.

## Ce que la décision coûte, sans atténuation

- **La promesse « couvrir tout le cycle » devient fausse** et disparaît partout où elle figure. Un
  différenciateur qu'on abandonne est un différenciateur en moins, pas une correction de rédaction.
- **Un concurrent couvre huit classes de risque que nous ne couvrirons pas**, et sort en six
  frameworks contre notre un. Mesuré, assumé ici.

## Ce que la décision achète

Toute l'énergie va à ce que la revue a nommé : **rendre vrai ce qui est déjà écrit, puis publier.**
Le périmètre n'a jamais été le facteur limitant.

## Ce qui ferait rouvrir cette décision

- des utilisateurs réels, déjà installés, qui demandent Discovery ou Run — pas un lecteur de README ;
- la capacité existante enfin prouvée : le motif principal de cette ADR tomberait.
