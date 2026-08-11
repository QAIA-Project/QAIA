Feature: Swag Labs - connexion, composition du panier et passage de commande

  Background:
    Given la boutique Swag Labs est disponible et son catalogue contient six articles

  # US-SD-01 / AC1 - condition: SD01-C1
  @QAIA-SD-001 @US-SD-01 @AC1 @P2 @e2e @ep
  Scenario: Un couple identifiant et mot de passe valide ouvre le catalogue
    Given un visiteur non connecte sur la page de connexion
    When il se connecte en tant que "standard_user" avec un mot de passe valide
    Then la page catalogue s'affiche avec ses six articles

  # US-SD-01 / AC1 - condition: SD01-C2
  # open: Q1 - le statut de defaut des profils publies n'est pas tranche
  @QAIA-SD-002 @US-SD-01 @AC1 @P2 @e2e @decision-table @low-confidence
  Scenario Outline: Chaque profil non verrouille atteint le catalogue
    Given un visiteur non connecte sur la page de connexion
    When il se connecte en tant que "<profil>" avec un mot de passe valide
    Then la page catalogue s'affiche avec ses six articles
    Examples:
      | profil                  |
      | standard_user           |
      | problem_user            |
      | performance_glitch_user |
      | error_user              |
      | visual_user             |

  # US-SD-01 / AC1 - condition: SD01-C3
  # open: Q1 - un budget de latence releve de perf-check, l'oracle retenu ici est fonctionnel
  @QAIA-SD-003 @US-SD-01 @AC1 @P2 @e2e @error-guessing @low-confidence
  Scenario: Le profil a latence degradee atteint quand meme le catalogue
    Given un visiteur non connecte sur la page de connexion
    When il se connecte en tant que "performance_glitch_user" avec un mot de passe valide
    Then la page catalogue s'affiche avec ses six articles

  # US-SD-01 / AC2 et AC3 - conditions: SD01-C4, SD01-C5, SD01-C6
  # La ligne "champ vide et mot de passe rempli" verifie la precedence exigee par AC2
  @QAIA-SD-004 @US-SD-01 @AC2 @AC3 @P1 @e2e @negative @decision-table
  Scenario Outline: Un champ d'authentification manquant est refuse en nommant le champ
    Given un visiteur non connecte sur la page de connexion
    When il soumet le formulaire avec l'identifiant "<identifiant>" et le mot de passe "<motdepasse>"
    Then le message "<message>" s'affiche
    Examples:
      | identifiant   | motdepasse | message                              |
      |               |            | Epic sadface: Username is required   |
      |               | rempli     | Epic sadface: Username is required   |
      | standard_user |            | Epic sadface: Password is required   |

  # US-SD-01 / AC4 - conditions: SD01-C7, SD01-C8, SD01-C9
  # L'oracle est l'indiscernabilite : trois classes d'echec, une seule sortie
  @QAIA-SD-005 @US-SD-01 @AC4 @P1 @e2e @negative @ep
  Scenario Outline: Un couple invalide est refuse sans reveler lequel des deux est faux
    Given un visiteur non connecte sur la page de connexion
    When il soumet le formulaire avec l'identifiant "<identifiant>" et un mot de passe <qualite>
    Then le message "Epic sadface: Username and password do not match any user in this service" s'affiche
    Examples:
      | identifiant      | qualite |
      | no_such_user_zzz | valide  |
      | standard_user    | errone  |
      | Standard_User    | valide  |

  # US-SD-01 / AC5 - condition: SD01-C10
  @QAIA-SD-006 @US-SD-01 @AC5 @P1 @e2e @negative @state-transition
  Scenario: Un compte verrouille est refuse par un message qui nomme le verrouillage
    Given un visiteur non connecte sur la page de connexion
    When il se connecte en tant que "locked_out_user" avec un mot de passe valide
    Then le message "Epic sadface: Sorry, this user has been locked out." s'affiche
    And la page catalogue ne s'affiche pas

  # US-SD-01 / AC5 et AC4 - condition: SD01-C11
  # open: Q5 - triplet AC1 x AC4 x AC5, aucune regle de la source ne tranche
  @QAIA-SD-007 @US-SD-01 @AC4 @AC5 @P1 @e2e @negative @decision-table @low-confidence
  Scenario: Un compte verrouille avec un mot de passe errone recoit le message generique
    Given un visiteur non connecte sur la page de connexion
    When il soumet le formulaire avec l'identifiant "locked_out_user" et un mot de passe errone
    Then le message "Epic sadface: Username and password do not match any user in this service" s'affiche

  # US-SD-01 / AC6 - condition: SD01-C12
  @QAIA-SD-008 @US-SD-01 @AC6 @P2 @e2e @error-guessing
  Scenario: L'identifiant saisi reste affiche apres un refus
    Given un visiteur non connecte sur la page de connexion
    When il soumet le formulaire avec l'identifiant "standard_user" et un mot de passe errone
    Then le champ identifiant contient encore "standard_user"

  # US-SD-01 / AC6 - condition: SD01-C13
  # open: Q3 - l'application contredit AC6, le critere ou l'application doit ceder
  @QAIA-SD-009 @US-SD-01 @AC6 @P2 @e2e @error-guessing @low-confidence
  Scenario: Le mot de passe saisi n'est pas vide apres un refus
    Given un visiteur non connecte sur la page de connexion
    When il soumet le formulaire avec l'identifiant "standard_user" et un mot de passe errone
    Then le champ mot de passe contient encore la valeur saisie

  # US-SD-01 / AC7 - condition: SD01-C14
  # Les trois pages protegees sont enumerees, pas seulement le catalogue
  @QAIA-SD-010 @US-SD-01 @AC7 @P1 @e2e @negative @ep
  Scenario Outline: Une page protegee atteinte sans session est refusee
    Given un visiteur non connecte
    When il demande la page "<page>" dans son navigateur
    Then un message d'acces refuse nommant "<page>" s'affiche
    And aucun contenu de cette page n'est visible
    Examples:
      | page                   |
      | /inventory.html        |
      | /cart.html             |
      | /checkout-step-two.html |

  # US-SD-01 / AC7 - condition: SD01-C15
  # open: Q11 - le statut HTTP n'est promis par aucune source, seule l'absence de donnees l'est
  @QAIA-SD-011 @US-SD-01 @AC7 @P1 @api @negative @ep @low-confidence
  Scenario: Une requete hors navigateur ne renvoie aucune donnee de catalogue
    Given aucun client authentifie
    When une requete HTTP GET est envoyee sur la route du catalogue sans session
    Then la reponse ne contient aucun libelle ni aucun prix d'article

  # US-SD-01 / AC7 - condition: SD01-C17
  @QAIA-SD-012 @US-SD-01 @AC7 @P1 @e2e @negative @state-transition
  Scenario: La deconnexion invalide la session et referme le catalogue
    Given un client connecte en tant que "standard_user"
    When il se deconnecte puis demande de nouveau la page catalogue
    Then un message d'acces refuse s'affiche

  # US-SD-02 / AC1 - condition: SD02-C1
  @QAIA-SD-013 @US-SD-02 @AC1 @P2 @e2e @boundary
  Scenario Outline: La pastille du panier compte les articles ajoutes jusqu'a la borne du catalogue
    Given un client connecte en tant que "standard_user" avec un panier vide
    When il ajoute <ajoutes> article(s) au panier
    Then la pastille du panier affiche "<pastille>"
    Examples:
      | ajoutes | pastille |
      | 1       | 1        |
      | 6       | 6        |

  # US-SD-02 / AC2 - condition: SD02-C2
  @QAIA-SD-014 @US-SD-02 @AC2 @P2 @e2e @state-transition
  Scenario: Le bouton d'un article ajoute devient Remove
    Given un client connecte en tant que "standard_user" avec un panier vide
    When il ajoute l'article "Sauce Labs Backpack" au panier
    Then le bouton de cet article porte le libelle "Remove"

  # US-SD-02 / AC3 - condition: SD02-C3
  @QAIA-SD-015 @US-SD-02 @AC3 @P2 @e2e @boundary
  Scenario: Retirer un article parmi deux decremente la pastille
    Given un client connecte en tant que "standard_user" avec deux articles au panier
    When il retire un article du panier
    Then la pastille du panier affiche "1"

  # US-SD-02 / AC3 - condition: SD02-C4 (borne basse)
  @QAIA-SD-016 @US-SD-02 @AC3 @P2 @e2e @boundary
  Scenario: Retirer le dernier article fait disparaitre la pastille
    Given un client connecte en tant que "standard_user" avec un seul article au panier
    When il retire cet article du panier
    Then aucune pastille de panier n'est affichee

  # US-SD-02 / AC2 - condition: SD02-C5
  # open: Q1 - fonction inoperante, ce n'est pas un refus donc pas un cas negatif
  @QAIA-SD-017 @US-SD-02 @AC2 @P2 @e2e @decision-table @low-confidence
  Scenario Outline: Sous certains profils le bouton Remove ne decremente pas la pastille
    Given un client connecte en tant que "<profil>" avec un seul article au panier
    When il retire cet article du panier
    Then la pastille du panier affiche encore "1"
    Examples:
      | profil       |
      | problem_user |
      | error_user   |

  # US-SD-02 / AC4 - condition: SD02-C6
  @QAIA-SD-018 @US-SD-02 @AC4 @P2 @e2e @ep
  Scenario: La ligne du panier reprend le libelle et le prix du catalogue
    Given un client connecte en tant que "standard_user" avec un panier vide
    When il ajoute l'article "Sauce Labs Backpack" affiche a "$29.99" puis ouvre son panier
    Then la ligne du panier porte le libelle "Sauce Labs Backpack" et le prix "$29.99"

  # US-SD-02 / AC4 - condition: SD02-C7
  # open: Q1 - relation metamorphique, aucun prix de reference n'est enoncable sous ce profil
  @QAIA-SD-019 @US-SD-02 @AC4 @P1 @e2e @metamorphic @low-confidence
  Scenario: Le prix d'un article est le meme sur la vignette, la fiche et la ligne du panier
    Given un client connecte en tant que "visual_user"
    When il releve le prix de "Sauce Labs Backpack" sur la vignette, sur sa fiche et dans le panier
    Then les trois prix releves sont identiques

  # US-SD-02 / AC4 - condition: SD02-C8
  # open: Q1
  @QAIA-SD-020 @US-SD-02 @AC4 @P2 @e2e @metamorphic @low-confidence
  Scenario: Le lien d'un article ouvre la fiche de l'article qu'il nomme
    Given un client connecte en tant que "problem_user"
    When il ouvre la fiche depuis le libelle "Sauce Labs Backpack" du catalogue
    Then la fiche ouverte porte le titre "Sauce Labs Backpack"

  # US-SD-02 / AC5 - condition: SD02-C9
  @QAIA-SD-021 @US-SD-02 @AC5 @P2 @e2e @state-transition
  Scenario: Le contenu du panier survit a un aller-retour vers une fiche article
    Given un client connecte en tant que "standard_user" avec deux articles au panier
    When il ouvre une fiche article puis revient au catalogue
    Then la pastille du panier affiche "2"

  # US-SD-02 / AC6 - condition: SD02-C10
  @QAIA-SD-022 @US-SD-02 @AC6 @P2 @e2e @ep
  Scenario Outline: Chaque option de tri classe le catalogue dans l'ordre annonce
    Given un client connecte en tant que "standard_user" sur le catalogue
    When il selectionne l'option de tri "<option>"
    Then le premier article affiche est "<premier>"
    Examples:
      | option              | premier                            |
      | Name (A to Z)       | Sauce Labs Backpack                |
      | Name (Z to A)       | Test.allTheThings() T-Shirt (Red)  |
      | Price (low to high) | Sauce Labs Onesie                  |
      | Price (high to low) | Sauce Labs Fleece Jacket           |

  # US-SD-02 / AC6 - condition: SD02-C11
  @QAIA-SD-023 @US-SD-02 @AC6 @P2 @e2e @state-transition
  Scenario: Trier le catalogue ne modifie pas le contenu du panier
    Given un client connecte en tant que "standard_user" avec deux articles au panier
    When il selectionne l'option de tri "Price (low to high)"
    Then la pastille du panier affiche encore "2"

  # US-SD-02 / AC6 - condition: SD02-C12
  # open: Q6 - la persistance du tri n'est specifiee nulle part
  @QAIA-SD-024 @US-SD-02 @AC6 @P2 @e2e @state-transition @low-confidence
  Scenario: Le tri selectionne ne survit pas a une navigation aller-retour
    Given un client connecte en tant que "standard_user" ayant trie le catalogue par "Price (high to low)"
    When il ouvre une fiche article puis revient au catalogue
    Then le selecteur de tri est revenu a "Name (A to Z)"

  # US-SD-02 / AC6 - condition: SD02-C13
  # open: Q1
  @QAIA-SD-025 @US-SD-02 @AC6 @P2 @e2e @decision-table @low-confidence
  Scenario Outline: Sous certains profils le selecteur de tri reste sans effet
    Given un client connecte en tant que "<profil>" sur le catalogue
    When il selectionne l'option de tri "Price (high to low)"
    Then l'ordre des articles est inchange
    Examples:
      | profil       |
      | problem_user |
      | error_user   |

  # Hors AC - condition: SD02-C14 (motif 3c "cycle de vie complet")
  # open: Q9 - la persistance du panier entre sessions n'est pas specifiee
  @QAIA-SD-026 @US-SD-02 @derived @P2 @e2e @state-transition @low-confidence
  Scenario: Le panier survit a une deconnexion suivie d'une reconnexion
    Given un client connecte en tant que "standard_user" avec un article au panier et qui s'est deconnecte
    When il se reconnecte en tant que "standard_user" avec un mot de passe valide
    Then la pastille du panier affiche "1"

  # Hors AC - condition: SD02-C15 (motif 3c "CRUD et inverses")
  # open: Q10 - le contrat de la remise a zero d'etat n'est pas specifie
  @QAIA-SD-027 @US-SD-02 @derived @P2 @e2e @crud @low-confidence
  Scenario: La remise a zero de l'etat vide le panier et l'affichage des articles suit
    Given un client connecte en tant que "standard_user" avec deux articles au panier
    When il declenche la remise a zero de l'etat de l'application
    Then aucune pastille de panier n'est affichee
    And aucun article du catalogue ne porte le libelle "Remove"

  # US-SD-03 / AC1 et AC2 - condition: SD03-C1
  # Les trois champs sont signales un a un : la precedence est l'objet du test
  @QAIA-SD-028 @US-SD-03 @AC1 @AC2 @P1 @e2e @negative @decision-table
  Scenario Outline: Un champ de livraison manquant est refuse en le nommant, un a la fois
    Given un client connecte en tant que "standard_user" avec un article au panier
    When il soumet le formulaire de livraison avec les champs deja remplis "<remplis>"
    Then le message "<message>" s'affiche
    Examples:
      | remplis        | message                        |
      | aucun          | Error: First Name is required  |
      | prenom         | Error: Last Name is required   |
      | prenom et nom  | Error: Postal Code is required |

  # US-SD-03 / AC1 - condition: SD03-C2
  # open: Q7 - "obligatoire" n'est pas defini : vide ou blanc
  @QAIA-SD-029 @US-SD-03 @AC1 @P2 @e2e @boundary @low-confidence
  Scenario: Trois champs de livraison remplis d'espaces sont acceptes
    Given un client connecte en tant que "standard_user" avec un article au panier
    When il soumet le formulaire de livraison avec trois champs ne contenant que des espaces
    Then le recapitulatif de commande s'affiche

  # US-SD-03 / AC3 - condition: SD03-C3
  @QAIA-SD-030 @US-SD-03 @AC3 @P3 @e2e @ep
  Scenario: Le recapitulatif affiche le sous-total, la taxe et le total
    Given un client connecte en tant que "standard_user" avec un article au panier
    When il valide le formulaire de livraison avec des donnees completes
    Then le recapitulatif affiche un sous-total, une taxe et un total

  # US-SD-03 / AC4 - condition: SD03-C4
  # Relation metamorphique : verifiee sur quatre paniers sans figer d'oracle de montant
  @QAIA-SD-031 @US-SD-03 @AC4 @P1 @e2e @metamorphic
  Scenario Outline: Le total est la somme du sous-total et de la taxe
    Given un client connecte en tant que "standard_user" dont le panier vaut "<soustotal>"
    When il ouvre le recapitulatif de commande
    Then le total affiche est egal a la somme du sous-total "<soustotal>" et de la taxe "<taxe>"
    Examples:
      | soustotal | taxe   |
      | $7.99     | $0.64  |
      | $49.99    | $4.00  |
      | $55.97    | $4.48  |
      | $129.94   | $10.40 |

  # US-SD-03 / AC5 - condition: SD03-C5
  # Valeurs calculees a 8 % puis observees ; l'egalite au demi-centime est demontree impossible (Q4)
  @QAIA-SD-032 @US-SD-03 @AC5 @P1 @e2e @boundary
  Scenario Outline: La taxe vaut huit pour cent du sous-total arrondi au centime
    Given un client connecte en tant que "standard_user" dont le panier vaut "<soustotal>"
    When il ouvre le recapitulatif de commande
    Then la taxe affichee est "<taxe>"
    Examples:
      | soustotal | taxe   |
      | $7.99     | $0.64  |
      | $49.99    | $4.00  |
      | $55.97    | $4.48  |
      | $129.94   | $10.40 |

  # US-SD-03 / AC6 - condition: SD03-C7
  @QAIA-SD-033 @US-SD-03 @AC6 @P2 @e2e @state-transition
  Scenario: Confirmer la commande affiche la confirmation et vide le panier
    Given un client connecte en tant que "standard_user" sur le recapitulatif d'un panier d'un article
    When il confirme la commande
    Then le message "Thank you for your order!" s'affiche
    And aucune pastille de panier n'est affichee

  # US-SD-03 / AC6 - condition: SD03-C8
  # open: Q8 - une soumission egale-t-elle une commande, la source ne le dit pas
  @QAIA-SD-034 @US-SD-03 @AC6 @P1 @e2e @state-transition @low-confidence
  Scenario: Le retour arriere apres confirmation rend le bouton de confirmation de nouveau actif
    Given un client connecte en tant que "standard_user" venant de confirmer une commande
    When il revient a la page precedente
    Then le bouton de confirmation de commande est de nouveau actionnable

  # US-SD-03 / AC6 - condition: SD03-C9
  # open: Q1
  @QAIA-SD-035 @US-SD-03 @AC6 @P2 @e2e @decision-table @low-confidence
  Scenario: Sous le profil en erreur la confirmation de commande reste sans effet
    Given un client connecte en tant que "error_user" sur le recapitulatif d'un panier d'un article
    When il confirme la commande
    Then le recapitulatif de commande est toujours affiche

  # US-SD-03 / AC6 - condition: SD03-C10
  # open: Q1
  @QAIA-SD-036 @US-SD-03 @AC6 @P2 @e2e @error-guessing @low-confidence
  Scenario: Sous le profil defectueux le champ nom rejette la saisie et bloque la commande
    Given un client connecte en tant que "problem_user" avec un article au panier
    When il saisit un prenom, un nom et un code postal dans le formulaire de livraison
    Then le champ nom est reste vide

  # US-SD-03 / AC7 - condition: SD03-C11
  # open: Q2 - AC7 exige un refus que l'application ne prononce pas ; ce scenario documente
  # la divergence, il n'exerce aucun refus et n'est donc pas compte comme cas negatif
  @QAIA-SD-037 @US-SD-03 @AC7 @P1 @e2e @ep @low-confidence
  Scenario: Un panier vide atteint la confirmation de commande avec un total nul
    Given un client connecte en tant que "standard_user" avec un panier vide
    When il deroule le tunnel de commande jusqu'a la confirmation
    Then le message "Thank you for your order!" s'affiche alors que le total etait "$0.00"

  # Hors AC - condition: SD03-C13 (motif 3c "contenu textuel imprevu")
  # open: Q7 - longueur et jeu de caracteres acceptes ne sont pas specifies
  @QAIA-SD-038 @US-SD-03 @derived @P2 @e2e @error-guessing @low-confidence
  Scenario: Le contenu exotique des champs de livraison est restitue comme donnee
    Given un client connecte en tant que "standard_user" avec un article au panier
    When il soumet le formulaire de livraison contenant du balisage, des caracteres non latins et trois cents caracteres
    Then le recapitulatif s'affiche sans interpreter le balisage saisi

  # Parcours de bout en bout - un seul par cahier, exclu du decompte d'atomicite
  @QAIA-SD-039 @US-SD-03 @AC6 @P1 @e2e @smoke
  Scenario: Parcours complet de la connexion a la commande confirmee
    Given un visiteur non connecte sur la page de connexion
    When il se connecte, ajoute un article, remplit la livraison et confirme la commande
    Then la commande est confirmee et le panier est vide
