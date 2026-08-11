/**
 * Scenarios @api — restful-booker, cahier `21-restfulbooker.feature` (38 blocs, 55 cas).
 *
 * L'etiquette de niveau est LUE, pas deduite : les 38 scenarios portent @api, aucun ne porte
 * @e2e, et le controle de coherence de forme (une requete + un statut) est d'accord avec
 * l'etiquette dans les 38 cas. Aucun desaccord a signaler (ADR 0008, etape 1b).
 *
 * Le cahier dit ce que la DOCUMENTATION PROMET, jamais ce que le service FAIT. Les scenarios
 * @low-confidence portent une question non arbitree (le contrat ne declare aucun code d'erreur) :
 * chaque test generes le rappelle dans son titre et dans un commentaire. UN ECHEC SUR UN TEST
 * @low-confidence REPOND A LA QUESTION OUVERTE — ne pas le "corriger" en alignant l'attendu sur
 * la reponse observee, ce qui promouvrait un constat en specification (self-review D5/D6).
 *
 * Assertions : statut d'abord, puis corps, puis en-tetes (api-steps.md).
 */
const { test, expect, CREDENTIALS, bookingPayload, omit } = require('../api-fixtures');

const BUSINESS_FIELDS = ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates', 'additionalneeds'];

test.describe('US-RB-01 — Obtenir un jeton d acces', () => {
  test('@QAIA-RB-001 @AC1 @P1 @api Des justificatifs valides renvoient un jeton', async ({ api }) => {
    const res = await api.post('/auth', { data: CREDENTIALS });

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(typeof body.token).toBe('string');
    expect(body.token.length).toBeGreaterThan(0);
  });

  for (const champ of ['password', 'username']) {
    test(`@QAIA-RB-002 @AC2 @P1 @api @low-confidence Des justificatifs dont "${champ}" est errone ne renvoient aucun jeton`, async ({ api }) => {
      // @low-confidence — open: Q1. Le contrat ne declare aucun code d'echec pour CreateToken,
      // le Then ne porte donc que sur l'ABSENCE de jeton.
      // Controle positif : @QAIA-RB-001 prouve que le meme appel renvoie bien un jeton avec des
      // justificatifs valides. Sans lui, ce test serait vert sur un service casse (self-review D7).
      const res = await api.post('/auth', { data: { ...CREDENTIALS, [champ]: 'valeur_erronee_qaia' } });

      const body = await res.json();
      expect(body.token).toBeUndefined();
    });
  }

  for (const champ of ['username', 'password']) {
    test(`@QAIA-RB-003 @AC2 @P1 @api @low-confidence Le champ "${champ}" omis du corps d authentification est refuse`, async ({ api }) => {
      // @low-confidence — open: Q6. Le 401 vient de la semantique HTTP appliquee a un parametre
      // declare `optional: false`, PAS d'un code declare par le contrat : c'est l'hypothese que
      // ce test met a l'epreuve.
      const res = await api.post('/auth', { data: omit(CREDENTIALS, champ) });

      expect(res.status()).toBe(401);
      const body = await res.json();
      expect(body.token).toBeUndefined();
    });
  }

  test('@QAIA-RB-004 @AC3 @P1 @api @low-confidence Le statut d une authentification refusee differe de celui d un succes', async ({ api }) => {
    // @low-confidence — open: Q1. Le CA est ecrit en sachant qu'il peut echouer : un client qui
    // teste `response.ok` doit pouvoir distinguer un refus d'un succes par le SEUL statut.
    const res = await api.post('/auth', { data: { ...CREDENTIALS, password: 'mauvais_mot_de_passe' } });

    expect(res.status()).toBe(401);
  });
});

test.describe('US-RB-02 — Creer une reservation', () => {
  test('@QAIA-RB-005 @AC1 @P1 @api Un corps complet cree la reservation et renvoie son identifiant', async ({ api }) => {
    const payload = bookingPayload();
    const res = await api.post('/booking', { data: payload });

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(typeof body.bookingid).toBe('number');
    expect(body.booking).toEqual(payload);
  });

  test('@QAIA-RB-006 @AC1 @P2 @api Une reservation se cree sans aucun justificatif', async ({ api }) => {
    const payload = bookingPayload();
    const res = await api.post('/booking', {
      data: payload,
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    });

    expect(res.status()).toBe(200);
    // le Then ne demande que le statut ; on verifie tout de meme que la creation a eu lieu,
    // sinon un 200 vide satisferait le scenario (self-review D7)
    expect(typeof (await res.json()).bookingid).toBe('number');
  });

  test('@QAIA-RB-007 @AC2 @P1 @api Une reservation creee est relisible avec les memes valeurs metier', async ({ api, booking }) => {
    const res = await api.get(`/booking/${booking.id}`);

    expect(res.status()).toBe(200);
    const body = await res.json();
    for (const field of BUSINESS_FIELDS) expect(body[field]).toEqual(booking.payload[field]);
  });

  for (const champ of ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates.checkin', 'bookingdates.checkout', 'additionalneeds']) {
    test(`@QAIA-RB-008 @AC3 @P1 @api @low-confidence Omettre le champ obligatoire "${champ}" a la creation est refuse`, async ({ api }) => {
      // @low-confidence — open: Q3. Le contrat declare le champ `optional: false` mais ne declare
      // AUCUN code d'erreur : le 400 est ce qu'un client a le droit d'attendre, pas une promesse
      // publiee. Le CA de la ligne de base ajoute : un refus, jamais une erreur serveur.
      const res = await api.post('/booking', { data: omit(bookingPayload(), champ) });

      expect(res.status()).toBe(400);
    });
  }

  test('@QAIA-RB-009 @AC3 @P1 @api @low-confidence Un corps de creation vide est refuse', async ({ api }) => {
    // @low-confidence — open: Q3.
    const res = await api.post('/booking', { data: {} });

    expect(res.status()).toBe(400);
  });

  for (const [champ, valeur] of [['totalprice', 'cent'], ['depositpaid', 'oui']]) {
    test(`@QAIA-RB-010 @AC3 @P2 @api @low-confidence Le champ "${champ}" envoye dans un type non declare est refuse`, async ({ api }) => {
      // @low-confidence — open: Q3.
      const res = await api.post('/booking', { data: bookingPayload({ [champ]: valeur }) });

      expect(res.status()).toBe(400);
    });
  }

  test('@QAIA-RB-011 @AC3 @P2 @api @low-confidence Une date de check-in hors du format CCYY-MM-DD est refusee', async ({ api }) => {
    // @low-confidence — open: Q5. Le format n'est enonce que dans la prose de GetBookings,
    // jamais dans le schema de CreateBooking.
    const res = await api.post('/booking', {
      data: bookingPayload({ bookingdates: { checkin: '01/01/2018', checkout: '2019-01-01' } }),
    });

    expect(res.status()).toBe(400);
  });

  test('@QAIA-RB-012 @AC5 @P1 @api Le statut declare d une creation est 200', async ({ api }) => {
    // L'oracle est le contrat publie ("Success 200"), PAS la semantique HTTP qui voudrait 201.
    const res = await api.post('/booking', { data: bookingPayload() });

    expect(res.status()).toBe(200);
  });

  test('@QAIA-RB-013 @AC6 @P2 @api Une creation en XML renvoie une reponse XML', async ({ api }) => {
    const p = bookingPayload();
    const xml = `<booking><firstname>${p.firstname}</firstname><lastname>${p.lastname}</lastname>`
      + `<totalprice>${p.totalprice}</totalprice><depositpaid>${p.depositpaid}</depositpaid>`
      + `<bookingdates><checkin>${p.bookingdates.checkin}</checkin><checkout>${p.bookingdates.checkout}</checkout></bookingdates>`
      + `<additionalneeds>${p.additionalneeds}</additionalneeds></booking>`;
    const res = await api.post('/booking', { headers: { 'Content-Type': 'text/xml' }, data: xml });

    expect(res.status()).toBe(200);
    const body = await res.text();
    expect(body).toContain('<created-booking>');
    expect(body).toContain(p.firstname);
  });

  test('@QAIA-RB-014 @AC6 @P3 @api @low-confidence Un type de contenu non supporte est refuse sans erreur serveur', async ({ api }) => {
    // @low-confidence — open: Q11. Aucune enumeration formelle de Content-Type n'est declaree ;
    // 415 est la reponse que la semantique HTTP prescrit.
    const res = await api.post('/booking', {
      headers: { 'Content-Type': 'text/plain' },
      data: JSON.stringify(bookingPayload()),
    });

    expect(res.status()).toBe(415);
  });

  for (const prix of [0, -1]) {
    test(`@QAIA-RB-015 @AC7 @P3 @api @low-confidence Un totalprice de ${prix}, hors du domaine metier, est refuse`, async ({ api }) => {
      // @low-confidence — open: Q3. `totalprice` est un Number SANS BORNE DECLAREE : la borne
      // metier (un prix strictement positif) est une attente, pas une clause du contrat.
      const res = await api.post('/booking', { data: bookingPayload({ totalprice: prix }) });

      expect(res.status()).toBe(400);
    });
  }
});

test.describe('US-RB-03 — Proteger les operations mutantes', () => {
  for (const methode of ['PUT', 'PATCH', 'DELETE']) {
    test(`@QAIA-RB-016 @AC1 @AC2 @AC3 @P1 @api @low-confidence Un ${methode} sans justificatif est refuse`, async ({ api, booking }) => {
      // @low-confidence — open: Q2. La reservation visee est CELLE CREEE PAR CE TEST : aucune
      // ressource tierce n'est touchee, y compris dans le cas ou le service accepterait l'appel.
      const res = await api.fetch(`/booking/${booking.id}`, {
        method: methode,
        data: methode === 'DELETE' ? undefined : booking.payload,
      });

      expect(res.status()).toBe(403);
    });
  }

  for (const methode of ['PUT', 'PATCH', 'DELETE']) {
    test(`@QAIA-RB-017 @AC3 @P2 @api @low-confidence Un ${methode} avec un jeton inconnu est refuse comme sans justificatif`, async ({ api, booking }) => {
      // @low-confidence — open: Q2.
      const res = await api.fetch(`/booking/${booking.id}`, {
        method: methode,
        headers: { Cookie: 'token=jeton_inconnu_du_service_qaia' },
        data: methode === 'DELETE' ? undefined : booking.payload,
      });

      expect(res.status()).toBe(403);
    });
  }

  test('@QAIA-RB-018 @AC4 @P1 @api Une modification refusee laisse la reservation inchangee', async ({ api, booking }) => {
    // mise en place : le refus doit avoir REELLEMENT eu lieu, sinon le Then serait verifie
    // contre un non-evenement (self-review D7).
    const refused = await api.put(`/booking/${booking.id}`, {
      data: { ...booking.payload, firstname: 'NeDoitPasEtreEcrit' },
    });
    expect(refused.status(), 'mise en place : la modification devait etre refusee').toBe(403);

    const res = await api.get(`/booking/${booking.id}`);

    expect(res.status()).toBe(200);
    const body = await res.json();
    for (const field of BUSINESS_FIELDS) expect(body[field]).toEqual(booking.payload[field]);
    expect(body.firstname).not.toBe('NeDoitPasEtreEcrit');
  });

  test('@QAIA-RB-019 @AC5 @P1 @api Une modification totale portant le jeton en cookie est acceptee', async ({ api, booking, token }) => {
    const modifie = { ...booking.payload, firstname: `${booking.payload.firstname}MOD`, totalprice: 222 };
    const res = await api.put(`/booking/${booking.id}`, {
      headers: { Cookie: `token=${token}` },
      data: modifie,
    });

    expect(res.status()).toBe(200);
    const body = await res.json();
    for (const field of BUSINESS_FIELDS) expect(body[field]).toEqual(modifie[field]);
  });

  test('@QAIA-RB-020 @AC5 @P1 @api Une modification totale portant une authentification Basic est acceptee', async ({ api, booking }) => {
    const basic = Buffer.from(`${CREDENTIALS.username}:${CREDENTIALS.password}`).toString('base64');
    const res = await api.put(`/booking/${booking.id}`, {
      headers: { Authorization: `Basic ${basic}` },
      data: { ...booking.payload, totalprice: 333 },
    });

    expect(res.status()).toBe(200);
  });

  test('@QAIA-RB-021 @AC6 @P2 @api @low-confidence Une modification totale amputee d un champ obligatoire est refusee', async ({ api, booking, token }) => {
    // @low-confidence — open: Q3. `firstname` est declare `optional: false` sur UpdateBooking,
    // mais aucun code d'erreur n'accompagne cette obligation.
    const res = await api.put(`/booking/${booking.id}`, {
      headers: { Cookie: `token=${token}` },
      data: omit(booking.payload, 'firstname'),
    });

    expect(res.status()).toBe(400);
  });

  test('@QAIA-RB-022 @AC7 @P1 @api Une modification partielle ne touche que le champ envoye', async ({ api, booking, token }) => {
    const nouveauPrenom = `${booking.payload.firstname}PATCH`;
    const res = await api.patch(`/booking/${booking.id}`, {
      headers: { Cookie: `token=${token}` },
      data: { firstname: nouveauPrenom },
    });

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.firstname).toBe(nouveauPrenom);
    for (const field of BUSINESS_FIELDS.filter((f) => f !== 'firstname')) {
      expect(body[field]).toEqual(booking.payload[field]);
    }
  });

  test('@QAIA-RB-023 @AC7 @P2 @api @low-confidence Une modification partielle a corps vide laisse la reservation inchangee', async ({ api, booking, token }) => {
    // @low-confidence — open: Q9. Tous les parametres de PartialUpdateBooking sont `optional: true`,
    // donc `{}` est un corps VALIDE au sens du contrat — c'est cette lecture qui est eprouvee.
    const res = await api.patch(`/booking/${booking.id}`, {
      headers: { Cookie: `token=${token}` },
      data: {},
    });

    const body = await res.json();
    for (const field of BUSINESS_FIELDS) expect(body[field]).toEqual(booking.payload[field]);
  });

  test('@QAIA-RB-024 @AC8 @P2 @api @low-confidence La suppression authentifiee d une reservation creee par le test renvoie 201', async ({ api, booking, token }) => {
    // @low-confidence — open: Q4. Le contrat se contredit : groupe "Success 200", exemple "201 Created".
    // Suppression AUTORISEE : la reservation a ete creee par ce test (consigne de campagne).
    const res = await api.delete(`/booking/${booking.id}`, { headers: { Cookie: `token=${token}` } });

    expect(res.status()).toBe(201);
  });

  test('@QAIA-RB-025 @AC8 @P2 @api @low-confidence Une reservation supprimee n est plus lisible', async ({ api, booking, token }) => {
    // @low-confidence — open: Q10. Aucun code d'absence n'est declare par GetBooking.
    const deleted = await api.delete(`/booking/${booking.id}`, { headers: { Cookie: `token=${token}` } });
    expect([200, 201], 'mise en place : la suppression devait aboutir').toContain(deleted.status());

    const res = await api.get(`/booking/${booking.id}`);

    expect(res.status()).toBe(404);
  });
});

test.describe('US-RB-04 — Lister et filtrer les reservations', () => {
  test('@QAIA-RB-026 @AC1 @P1 @api La liste sans filtre renvoie des identifiants de reservation', async ({ api, readOnlyBooking }) => {
    const res = await api.get('/booking');

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
    for (const item of body.slice(0, 50)) expect(typeof item.bookingid).toBe('number');
    // la reservation creee par ce worker existe : le tableau n'est pas un vestige
    expect(body.some((b) => b.bookingid === readOnlyBooking.id)).toBe(true);
  });

  for (const filtre of ['firstname', 'lastname', 'checkin', 'checkout']) {
    test(`@QAIA-RB-027 @AC2 @P2 @api Le filtre declare "${filtre}" restreint la liste`, async ({ api, readOnlyBooking }) => {
      const p = readOnlyBooking.payload;
      const valeur = filtre === 'checkin' ? p.bookingdates.checkin
        : filtre === 'checkout' ? p.bookingdates.checkout
          : p[filtre];
      const res = await api.get(`/booking?${filtre}=${encodeURIComponent(valeur)}`);

      expect(res.status()).toBe(200);
      const body = await res.json();
      expect(body.some((b) => b.bookingid === readOnlyBooking.id)).toBe(true);
    });
  }

  test('@QAIA-RB-028 @AC2 @P2 @api Les quatre filtres combines restreignent la liste conjointement', async ({ api, readOnlyBooking }) => {
    const p = readOnlyBooking.payload;
    const qs = new URLSearchParams({
      firstname: p.firstname, lastname: p.lastname,
      checkin: p.bookingdates.checkin, checkout: p.bookingdates.checkout,
    });
    const res = await api.get(`/booking?${qs}`);

    const body = await res.json();
    expect(body.some((b) => b.bookingid === readOnlyBooking.id)).toBe(true);
  });

  test('@QAIA-RB-029 @AC3 @P2 @api @low-confidence Un filtre de check-in egal a la date de la reservation l inclut', async ({ api, readOnlyBooking }) => {
    // @low-confidence — open: Q12. Le "greater than or equal to" ne vit que dans la prose de
    // la documentation, jamais dans le schema : la borne INCLUSIVE est l'hypothese eprouvee ici.
    const res = await api.get(`/booking?checkin=${readOnlyBooking.payload.bookingdates.checkin}`);

    const body = await res.json();
    expect(body.some((b) => b.bookingid === readOnlyBooking.id)).toBe(true);
  });

  test('@QAIA-RB-030 @AC3 @P2 @api @low-confidence Un filtre de date hors du format CCYY-MM-DD est refuse', async ({ api }) => {
    // @low-confidence — open: Q5. "Format must be CCYY-MM-DD" est de la prose, pas un schema.
    const res = await api.get('/booking?checkin=13/03/2014');

    expect(res.status()).toBe(400);
  });

  test('@QAIA-RB-031 @AC4 @P2 @api Un filtre sans correspondance renvoie un tableau vide', async ({ api }) => {
    const res = await api.get('/booking?firstname=AucunPrenomQAIANeCorrespondJamais');

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body).toEqual([]);
  });

  test('@QAIA-RB-032 @AC5 @P3 @api @low-confidence Un parametre de requete inconnu est ignore', async ({ api, readOnlyBooking }) => {
    // @low-confidence — open: Q14. Aucun parametre inconnu n'est declare par le contrat.
    // NOTE DE FRAGILITE : les deux appels portent sur un service PUBLIC dont la liste bouge
    // avec les creations d'autres utilisateurs. Une divergence entre les deux corps peut donc
    // signaler une concurrence plutot que le comportement teste — candidat @quarantine si
    // `flaky-detect` le confirme sur 3 runs. On borne le risque en filtrant sur une
    // reservation connue au lieu de comparer la liste globale.
    const filtre = `firstname=${encodeURIComponent(readOnlyBooking.payload.firstname)}`;
    const sans = await api.get(`/booking?${filtre}`);
    const avec = await api.get(`/booking?${filtre}&parametre_inconnu_qaia=42`);

    expect(avec.status()).toBe(sans.status());
    expect(await avec.json()).toEqual(await sans.json());
  });
});

test.describe('US-RB-05 — Lire une reservation par identifiant', () => {
  test('@QAIA-RB-033 @AC1 @P1 @api Une lecture par identifiant renvoie les champs declares', async ({ api, readOnlyBooking }) => {
    const res = await api.get(`/booking/${readOnlyBooking.id}`);

    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Object.keys(body).sort()).toEqual(
      ['additionalneeds', 'bookingdates', 'depositpaid', 'firstname', 'lastname', 'totalprice'].sort(),
    );
    expect(Object.keys(body.bookingdates).sort()).toEqual(['checkin', 'checkout']);
  });

  test('@QAIA-RB-034 @AC2 @P1 @api @low-confidence Une lecture sur un identifiant inexistant est refusee', async ({ api }) => {
    // @low-confidence — open: Q10.
    const res = await api.get('/booking/99999999');

    expect(res.status()).toBe(404);
  });

  test('@QAIA-RB-035 @AC3 @P2 @api @low-confidence Une lecture sur un identifiant non numerique est refusee', async ({ api }) => {
    // @low-confidence — open: Q8. GetBooking declare `id` en String, UpdateBooking en Number :
    // le contrat se contredit, l'attendu 404 est une lecture parmi deux.
    const res = await api.get('/booking/abc');

    expect(res.status()).toBe(404);
  });

  test('@QAIA-RB-036 @AC4 @P2 @api Une lecture demandant du XML renvoie un document XML', async ({ api, readOnlyBooking }) => {
    const res = await api.get(`/booking/${readOnlyBooking.id}`, { headers: { Accept: 'application/xml' } });

    expect(res.status()).toBe(200);
    const body = await res.text();
    expect(body).toContain('<booking>');
    expect(body).toContain(readOnlyBooking.payload.firstname);
  });
});

test.describe('US-RB-06 — Controle de sante et surface protocolaire', () => {
  test('@QAIA-RB-037 @AC1 @P1 @api @low-confidence Le controle de sante renvoie le statut promis par son exemple', async ({ api }) => {
    // @low-confidence — open: Q4. Le bloc de succes se contredit : titre "Success 200",
    // description et exemple "201 Created". Le cahier a tranche pour l'exemple.
    const res = await api.get('/ping');

    expect(res.status()).toBe(201);
  });

  test('@QAIA-RB-038 @AC2 @P3 @api @low-confidence Une methode non declaree sur un chemin valide est refusee comme telle', async ({ api }) => {
    // @low-confidence — open: Q15. Le contrat ne declare que GET sur /ping ; 405 est ce que
    // la semantique HTTP prescrit pour une methode non permise sur une ressource existante.
    const res = await api.post('/ping', { data: {} });

    expect(res.status()).toBe(405);
  });
});
