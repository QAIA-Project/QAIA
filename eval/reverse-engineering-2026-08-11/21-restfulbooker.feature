Feature: restful-booker - contrat publie de l'API de reservation

  # Source : documentation apidoc de restful-booker (api_data.json, apidoc 0.25.0,
  # projet 1.0.0, genere le 2025-06-11). Conception : 20-restfulbooker-03-design.md.
  # Chaque scenario dit ce que la documentation PROMET, jamais ce que le service FAIT
  # (openapi-ingest : "a specification is a promise, not a fact"). Aucune requete n'a ete
  # emise pour produire ce cahier ; confirmer ou infirmer releve de contract-probe.
  # Les 22 scenarios @low-confidence reposent sur une question non arbitree : le contrat
  # ne declare AUCUN code d'erreur sur aucune de ses huit operations.

  # AC1 - POST /auth, operation CreateToken
  @QAIA-RB-001 @AC1 @P1 @api @ep
  Scenario: Des justificatifs valides renvoient un jeton
    # contract: CreateToken · success.200.token
    # condition: RB01-AC1-C1
    Given des justificatifs d'API valides
    When le client POST /auth avec ces justificatifs
    Then le statut de la reponse est 200
    And le corps de la reponse porte un champ "token" de type chaine

  # AC2 - la classe invalide des justificatifs
  @QAIA-RB-002 @AC2 @P1 @api @negative @ep @low-confidence
  Scenario Outline: Des justificatifs invalides ne renvoient aucun jeton
    # contract: CreateToken · success.200.token, par contraposee
    # condition: RB01-AC2-C1, RB01-AC2-C2
    # open: Q1
    Given des justificatifs d'API dont le champ "<champ>" est errone
    When le client POST /auth avec ces justificatifs
    Then le corps de la reponse ne porte aucun champ "token"

    Examples:
      | champ    |
      | password |
      | username |

  @QAIA-RB-003 @AC2 @P1 @api @negative @ep @low-confidence
  Scenario Outline: Un champ obligatoire absent du corps d'authentification est refuse
    # contract: CreateToken · parameter.username, parameter.password (optional: false)
    # condition: RB01-AC2-C3, RB01-AC2-C4
    # open: Q6
    Given des justificatifs d'API valides
    When le client POST /auth avec le champ "<champ>" omis du corps
    Then le statut de la reponse est 401
    And le corps de la reponse ne porte aucun champ "token"

    Examples:
      | champ    |
      | username |
      | password |

  # AC3 - contradiction 3 : aucun code d'echec n'est declare pour CreateToken
  @QAIA-RB-004 @AC3 @P1 @api @negative @ep @low-confidence
  Scenario: Le statut d'une authentification refusee differe de celui d'un succes
    # contract: CreateToken · aucun bloc error declare
    # condition: RB01-AC3-C1
    # open: Q1
    Given des justificatifs d'API dont le mot de passe est errone
    When le client POST /auth avec ces justificatifs
    Then le statut de la reponse est 401

  # AC1 - POST /booking, operation CreateBooking
  @QAIA-RB-005 @AC1 @P1 @api @ep
  Scenario: Un corps complet cree la reservation et renvoie son identifiant
    # contract: CreateBooking · success.200.bookingid, success.200.booking
    # condition: RB02-AC1-C1
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec ce corps
    Then le statut de la reponse est 200
    And le corps de la reponse porte un champ "bookingid" de type nombre
    And l'objet "booking" de la reponse reprend les sept champs envoyes

  @QAIA-RB-006 @AC1 @P2 @api @ep
  Scenario: Une reservation se cree sans aucun justificatif
    # contract: CreateBooking · aucun en-tete d'authentification declare
    # condition: RB02-AC1-C2
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec ce corps et sans en-tete Cookie ni Authorization
    Then le statut de la reponse est 200

  # AC2 - relecture apres creation
  @QAIA-RB-007 @AC2 @P1 @api @crud
  Scenario: Une reservation creee est relisible avec les memes valeurs metier
    # contract: GetBooking · success.200 (firstname, lastname, totalprice, depositpaid,
    # bookingdates.checkin, bookingdates.checkout, additionalneeds)
    # condition: RB02-AC2-C1
    Given une reservation creee par ce test et son identifiant
    When le client GET /booking/{id} pour cet identifiant
    Then le statut de la reponse est 200
    And les sept champs metier de la reponse valent ceux envoyes a la creation

  # AC3 - un chemin de refus par champ obligatoire (table de derivation, ligne "required")
  @QAIA-RB-008 @AC3 @P1 @api @negative @ep @low-confidence
  Scenario Outline: Omettre un champ obligatoire a la creation est refuse
    # contract: CreateBooking · parameter.<champ> (optional: false), aucun code d'erreur declare
    # condition: RB02-AC3-C1
    # open: Q3
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec le champ "<champ>" omis du corps
    Then le statut de la reponse est 400

    Examples:
      | champ                  |
      | firstname              |
      | lastname               |
      | totalprice             |
      | depositpaid            |
      | bookingdates.checkin   |
      | bookingdates.checkout  |
      | additionalneeds        |

  @QAIA-RB-009 @AC3 @P1 @api @negative @ep @low-confidence
  Scenario: Un corps de creation vide est refuse
    # contract: CreateBooking · parameter.* (sept champs optional: false)
    # condition: RB02-AC3-C2
    # open: Q3
    Given un client de l'API sans justificatif
    When le client POST /booking avec un corps JSON vide
    Then le statut de la reponse est 400

  @QAIA-RB-010 @AC3 @P2 @api @negative @ep @low-confidence
  Scenario Outline: Un champ envoye dans un type non declare est refuse
    # contract: CreateBooking · parameter.totalprice (Number), parameter.depositpaid (Boolean)
    # condition: RB02-AC3-C3
    # open: Q3
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec le champ "<champ>" valant la chaine "<valeur>"
    Then le statut de la reponse est 400

    Examples:
      | champ       | valeur |
      | totalprice  | cent   |
      | depositpaid | oui    |

  @QAIA-RB-011 @AC3 @P2 @api @negative @ep @low-confidence
  Scenario: Une date de check-in hors du format CCYY-MM-DD est refusee
    # contract: CreateBooking · parameter.bookingdates.checkin (type Date, format enonce
    # uniquement dans la prose de GetBookings · parameter.checkin)
    # condition: RB02-AC3-C4
    # open: Q5
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec un check-in valant "01/01/2018"
    Then le statut de la reponse est 400

  # AC5 - le contrat declare 200 pour une creation ; la semantique HTTP n'est pas l'oracle
  @QAIA-RB-012 @AC5 @P1 @api @ep
  Scenario: Le statut declare d'une creation est 200
    # contract: CreateBooking · success (groupe "Success 200")
    # condition: RB02-AC5-C1
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec ce corps
    Then le statut de la reponse est 200

  # AC6 - negociation de contenu
  @QAIA-RB-013 @AC6 @P2 @api @ep
  Scenario: Une creation en XML renvoie une reponse XML
    # contract: CreateBooking · header.Content-Type, success.examples (XML Response)
    # condition: RB02-AC6-C1
    Given un corps de reservation XML portant les sept champs obligatoires
    When le client POST /booking avec l'en-tete Content-Type "text/xml"
    Then le statut de la reponse est 200
    And le corps de la reponse est un document XML "created-booking"

  @QAIA-RB-014 @AC6 @P3 @api @negative @error-guessing @low-confidence
  Scenario: Un type de contenu non supporte est refuse sans erreur serveur
    # contract: CreateBooking · header.Content-Type, aucune enumeration formelle declaree
    # condition: RB02-AC6-C2
    # open: Q11
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec l'en-tete Content-Type "text/plain"
    Then le statut de la reponse est 415

  # AC7 - totalprice est un Number sans borne declaree
  @QAIA-RB-015 @AC7 @P3 @api @negative @boundary @low-confidence
  Scenario Outline: Un prix total hors du domaine metier est refuse
    # contract: CreateBooking · parameter.totalprice (Number, aucune borne declaree)
    # condition: RB02-AC7-C1
    # open: Q3
    Given un corps de reservation portant les sept champs obligatoires
    When le client POST /booking avec un totalprice valant <prix>
    Then le statut de la reponse est 400

    Examples:
      | prix |
      | 0    |
      | -1   |

  # AC1, AC2, AC3 - table de decision : mecanisme d'authentification x operation mutante
  @QAIA-RB-016 @AC1 @AC2 @AC3 @P1 @api @negative @decision-table @low-confidence
  Scenario Outline: Une operation mutante sans justificatif est refusee
    # contract: UpdateBooking, PartialUpdateBooking, DeleteBooking · header.Cookie,
    # header.Authorization, description ("Requires an authorization token")
    # condition: RB03-AC1-C1, RB03-AC2-C1, RB03-AC3-C1
    # open: Q2
    Given une reservation creee par ce test et son identifiant
    When le client envoie une requete <methode> sur /booking/{id} sans en-tete Cookie ni Authorization
    Then le statut de la reponse est 403

    Examples:
      | methode |
      | PUT     |
      | PATCH   |
      | DELETE  |

  @QAIA-RB-017 @AC3 @P2 @api @negative @decision-table @low-confidence
  Scenario Outline: Une operation mutante avec un justificatif invalide est refusee comme sans justificatif
    # contract: UpdateBooking, PartialUpdateBooking, DeleteBooking · header.Cookie
    # condition: RB03-AC3-C2
    # open: Q2
    Given une reservation creee par ce test et son identifiant
    When le client envoie une requete <methode> sur /booking/{id} avec un jeton inconnu du service
    Then le statut de la reponse est 403

    Examples:
      | methode |
      | PUT     |
      | PATCH   |
      | DELETE  |

  # AC4 - un refus n'a aucun effet de bord
  @QAIA-RB-018 @AC4 @P1 @api @negative @crud
  Scenario: Une modification refusee laisse la reservation inchangee
    # contract: GetBooking · success.200
    # condition: RB03-AC4-C1
    Given une reservation creee par ce test dont une modification sans justificatif a ete refusee
    When le client GET /booking/{id} pour cet identifiant
    Then les sept champs metier de la reponse valent ceux envoyes a la creation

  # AC5 - les deux mecanismes d'authentification declares
  @QAIA-RB-019 @AC5 @P1 @api @ep
  Scenario: Une modification totale portant le jeton en cookie est acceptee
    # contract: UpdateBooking · header.Cookie (token=<token_value>), success.200
    # condition: RB03-AC5-C1
    Given une reservation creee par ce test et un jeton d'API valide
    When le client PUT /booking/{id} avec un corps complet et l'en-tete Cookie portant ce jeton
    Then le statut de la reponse est 200
    And le corps de la reponse porte les sept champs metier modifies

  @QAIA-RB-020 @AC5 @P1 @api @ep
  Scenario: Une modification totale portant une authentification Basic est acceptee
    # contract: UpdateBooking · header.Authorization (Basic), examples (XML, URLencoded)
    # condition: RB03-AC5-C2
    Given une reservation creee par ce test et des justificatifs d'API valides
    When le client PUT /booking/{id} avec un corps complet et l'en-tete Authorization Basic
    Then le statut de la reponse est 200

  # AC6 - PUT exige les sept champs, contrairement a PATCH
  @QAIA-RB-021 @AC6 @P2 @api @negative @ep @low-confidence
  Scenario: Une modification totale amputee d'un champ obligatoire est refusee
    # contract: UpdateBooking · parameter.firstname (optional: false)
    # condition: RB03-AC6-C1
    # open: Q3
    Given une reservation creee par ce test et un jeton d'API valide
    When le client PUT /booking/{id} avec le champ "firstname" omis du corps
    Then le statut de la reponse est 400

  # AC7 - PATCH : tous les champs sont optionnels
  @QAIA-RB-022 @AC7 @P1 @api @crud
  Scenario: Une modification partielle ne touche que le champ envoye
    # contract: PartialUpdateBooking · parameter.* (optional: true), success.200
    # condition: RB03-AC7-C1
    Given une reservation creee par ce test et un jeton d'API valide
    When le client PATCH /booking/{id} avec le seul champ "firstname"
    Then le statut de la reponse est 200
    And les six autres champs metier de la reponse valent ceux envoyes a la creation

  @QAIA-RB-023 @AC7 @P2 @api @crud @low-confidence
  Scenario: Une modification partielle a corps vide laisse la reservation inchangee
    # contract: PartialUpdateBooking · parameter.* (tous optional: true, donc {} est valide)
    # condition: RB03-AC7-C2
    # open: Q9
    Given une reservation creee par ce test et un jeton d'API valide
    When le client PATCH /booking/{id} avec un corps JSON vide
    Then les sept champs metier de la reponse valent ceux envoyes a la creation

  # AC8 - suppression, et son inverse
  @QAIA-RB-024 @AC8 @P2 @api @crud @low-confidence
  Scenario: La suppression authentifiee d'une reservation creee par le test renvoie 201
    # contract: DeleteBooking · success (groupe "Success 200", description et exemple "201 Created")
    # condition: RB03-AC8-C1
    # open: Q4
    Given une reservation creee par ce test et un jeton d'API valide
    When le client DELETE /booking/{id} avec l'en-tete Cookie portant ce jeton
    Then le statut de la reponse est 201

  @QAIA-RB-025 @AC8 @P2 @api @negative @crud @low-confidence
  Scenario: Une reservation supprimee n'est plus lisible
    # contract: GetBooking · aucun code d'absence declare
    # condition: RB03-AC8-C2
    # open: Q10
    Given une reservation creee puis supprimee par ce test et son identifiant
    When le client GET /booking/{id} pour cet identifiant
    Then le statut de la reponse est 404

  # AC1 - GET /booking, operation GetBookings
  @QAIA-RB-026 @AC1 @P1 @api @ep
  Scenario: La liste sans filtre renvoie des identifiants de reservation
    # contract: GetBookings · success.200.object, success.200.object.bookingid
    # condition: RB04-AC1-C1
    Given au moins une reservation existante
    When le client GET /booking sans parametre de requete
    Then le statut de la reponse est 200
    And le corps de la reponse est un tableau dont chaque element porte un "bookingid" de type nombre

  # AC2 - quatre parametres de filtre optionnels
  @QAIA-RB-027 @AC2 @P2 @api @ep
  Scenario Outline: Chaque filtre declare restreint la liste
    # contract: GetBookings · parameter.firstname, parameter.lastname, parameter.checkin,
    # parameter.checkout (optional: true)
    # condition: RB04-AC2-C1
    Given une reservation creee par ce test dont les valeurs de filtre sont connues
    When le client GET /booking avec le seul parametre "<filtre>"
    Then le statut de la reponse est 200
    And le tableau de la reponse contient l'identifiant de cette reservation

    Examples:
      | filtre    |
      | firstname |
      | lastname  |
      | checkin   |
      | checkout  |

  @QAIA-RB-028 @AC2 @P2 @api @pairwise
  Scenario: Les quatre filtres combines restreignent la liste conjointement
    # contract: GetBookings · parameter.firstname, parameter.lastname, parameter.checkin,
    # parameter.checkout
    # condition: RB04-AC2-C2
    Given une reservation creee par ce test dont les valeurs de filtre sont connues
    When le client GET /booking avec les quatre parametres renseignes depuis cette reservation
    Then le tableau de la reponse contient l'identifiant de cette reservation

  # AC3 - la frontiere du filtre de date vit dans la prose, pas dans le schema
  @QAIA-RB-029 @AC3 @P2 @api @boundary @low-confidence
  Scenario: Un filtre de check-in egal a la date de la reservation l'inclut
    # contract: GetBookings · parameter.checkin ("greater than or equal to", prose seule)
    # condition: RB04-AC3-C1
    # open: Q12
    Given une reservation creee par ce test dont la date de check-in est connue
    When le client GET /booking avec le parametre checkin egal a cette date
    Then le tableau de la reponse contient l'identifiant de cette reservation

  @QAIA-RB-030 @AC3 @P2 @api @negative @ep @low-confidence
  Scenario: Un filtre de date hors du format CCYY-MM-DD est refuse
    # contract: GetBookings · parameter.checkin ("Format must be CCYY-MM-DD", prose seule)
    # condition: RB04-AC3-C2
    # open: Q5
    Given au moins une reservation existante
    When le client GET /booking avec le parametre checkin valant "13/03/2014"
    Then le statut de la reponse est 400

  # AC4 - un resultat vide n'est PAS un refus (negative-ratio.md, definition fermee)
  @QAIA-RB-031 @AC4 @P2 @api @ep
  Scenario: Un filtre sans correspondance renvoie un tableau vide
    # contract: GetBookings · success.200.object
    # condition: RB04-AC4-C1
    Given au moins une reservation existante
    When le client GET /booking avec un firstname qu'aucune reservation ne porte
    Then le statut de la reponse est 200
    And le corps de la reponse est un tableau vide

  # AC5 - surface protocolaire : la source est muette, l'issue reste ouverte
  @QAIA-RB-032 @AC5 @P3 @api @error-guessing @low-confidence
  Scenario: Un parametre de requete inconnu est ignore
    # contract: GetBookings · aucun parametre inconnu declare
    # condition: RB04-AC5-C1
    # open: Q14
    Given au moins une reservation existante
    When le client GET /booking avec un parametre de requete non declare
    Then le corps de la reponse est identique a celui obtenu sans ce parametre

  # AC1 - GET /booking/:id, operation GetBooking
  @QAIA-RB-033 @AC1 @P1 @api @ep
  Scenario: Une lecture par identifiant renvoie les champs declares
    # contract: GetBooking · success.200 (huit champs declares)
    # condition: RB05-AC1-C1
    Given une reservation creee par ce test et son identifiant
    When le client GET /booking/{id} pour cet identifiant
    Then le statut de la reponse est 200
    And le corps de la reponse porte les huit champs declares par le contrat

  @QAIA-RB-034 @AC2 @P1 @api @negative @ep @low-confidence
  Scenario: Une lecture sur un identifiant inexistant est refusee
    # contract: GetBooking · aucun code d'absence declare
    # condition: RB05-AC2-C1
    # open: Q10
    Given un identifiant de reservation qui n'existe pas
    When le client GET /booking/{id} pour cet identifiant
    Then le statut de la reponse est 404

  @QAIA-RB-035 @AC3 @P2 @api @negative @ep @low-confidence
  Scenario: Une lecture sur un identifiant non numerique est refusee
    # contract: GetBooking · parameter.id (String) contre UpdateBooking · parameter.id (Number)
    # condition: RB05-AC3-C1
    # open: Q8
    Given un client de l'API sans justificatif
    When le client GET /booking/abc
    Then le statut de la reponse est 404

  @QAIA-RB-036 @AC4 @P2 @api @ep
  Scenario: Une lecture demandant du XML renvoie un document XML
    # contract: GetBooking · header.Accept, success.examples (XML Response)
    # condition: RB05-AC4-C1
    Given une reservation creee par ce test et son identifiant
    When le client GET /booking/{id} avec l'en-tete Accept "application/xml"
    Then le statut de la reponse est 200
    And le corps de la reponse est un document XML "booking"

  # AC1 - GET /ping : le bloc de succes se contredit lui-meme (200 en titre, 201 en exemple)
  @QAIA-RB-037 @AC1 @P1 @api @ep @low-confidence
  Scenario: Le controle de sante renvoie le statut promis par son exemple
    # contract: Ping · success (groupe "Success 200", description et exemple "201 Created")
    # condition: RB06-AC1-C1
    # open: Q4
    Given un client de l'API sans justificatif
    When le client GET /ping
    Then le statut de la reponse est 201

  @QAIA-RB-038 @AC2 @P3 @api @negative @error-guessing @low-confidence
  Scenario: Une methode non declaree sur un chemin valide est refusee comme telle
    # contract: Ping · aucune methode autre que GET declaree
    # condition: RB06-AC2-C1
    # open: Q15
    Given un client de l'API sans justificatif
    When le client POST /ping
    Then le statut de la reponse est 405
