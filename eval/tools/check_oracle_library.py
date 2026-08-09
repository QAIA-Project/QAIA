#!/usr/bin/env python3
"""Verifie les affirmations calculables de la bibliotheque d'oracles.

## Pourquoi ce fichier existe

`oracle-generate` existe pour que les valeurs attendues d'un cahier de test soient **derivees
d'un standard plutot qu'inventees**. Sa bibliotheque (`oracles/library.md`) affirme des cas
canoniques : tel PAN est Luhn-valide, tel IBAN passe le mod-97, telle date est impossible.

Ces affirmations sont la racine de tout ce que la skill produit. Une seule fausse et **chaque
cahier genere depuis ce domaine porte une valeur attendue erronee** -- et elle se lira comme
« derivee d'un standard », donc personne ne la rediscutera. C'est la pire forme de defaut que ce
projet puisse livrer : une erreur qui emprunte l'autorite d'une norme.

Or elles sont **calculables**. Luhn est une somme ponderee, le mod-97 est une division, une date
impossible se detecte avec le calendrier. Aucun jugement, aucun reseau, aucune interpretation --
donc aucune raison de les croire sur parole.

Ce qui n'est PAS verifie ici : ce qui demande un registre externe (ISO 4217, ISO 3166) ou une
lecture de grammaire (RFC 5322). Ces domaines sont listes en fin de sortie comme **non couverts**
plutot que passes sous silence -- un controle partiel qui se tait sur son perimetre se lit comme
un controle complet.

Run: python eval/tools/check_oracle_library.py
Exit 0 toutes les affirmations calculables tiennent, 1 au moins une est fausse, 2 fichier illisible.
"""
import io
import os
import re
import sys

NL = chr(10)

LIB = os.path.join("plugins", "qaia-core", "skills", "oracle-generate", "oracles", "library.md")


def luhn_ok(number):
    digits = [int(c) for c in number if c.isdigit()]
    if not digits:
        return False
    total, parity = 0, len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def iban_ok(iban):
    s = re.sub(r"\s+", "", iban)
    if not re.match(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]+$", s):
        return False
    rearranged = s[4:] + s[:4]
    digits = "".join(str(int(c, 36)) for c in rearranged)
    return int(digits) % 97 == 1


def date_ok(text):
    """`YYYY-MM-DD` ou ordinale `YYYY-DDD`. Retourne True si la date existe."""
    import datetime
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", text)
    if m:
        y, mo, d = (int(g) for g in m.groups())
        try:
            datetime.date(y, mo, d)
            return True
        except ValueError:
            return False
    m = re.match(r"^(\d{4})-(\d{3})$", text)
    if m:
        y, doy = int(m.group(1)), int(m.group(2))
        last = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
        return 1 <= doy <= last
    return None


# Les affirmations, recopiees du fichier et re-lues depuis lui pour qu'elles ne puissent pas
# diverger en silence : chaque valeur doit etre PRESENTE dans library.md, sinon le controle
# verifie une bibliotheque qui n'existe plus.
CLAIMS = {
    # `XXX` a ete retire des affirmations "invalide" de la bibliotheque : il EST assigne
    # par ISO 4217 (transactions sans devise). Le classer invalide etait une erreur.
    "Luhn valide": (luhn_ok, True, ["4111 1111 1111 1111", "4012 8888 8888 1881",
                                    "5555 5555 5555 4444", "3782 822463 10005",
                                    "6011 1111 1111 1117"]),
    "Luhn invalide": (luhn_ok, False, ["4111 1111 1111 1112", "1234 5678 9012 3456",
                                       "0000 0000 0000 0001"]),
    "IBAN valide": (iban_ok, True, ["FR14 2004 1010 0505 0001 3M02 606"]),
    "date valide": (date_ok, True, ["2024-02-29"]),
    "date impossible": (date_ok, False, ["2023-02-29", "2100-02-29", "2023-04-31", "2023-366"]),
}

def parse_computable_claims(text):
    """Lit les paniers valide/invalide DEPUIS library.md.

    Ils etaient codes en dur : echanger les deux listes Luhn dans le fichier laissait le
    controle vert. Chaque valeur est desormais classee par la ligne qui la porte, et une
    section dont aucun panier n'est lisible est signalee plutot que silencieusement ignoree.
    """
    out = {"Luhn valide": (luhn_ok, True, []), "Luhn invalide": (luhn_ok, False, []),
           "IBAN valide": (iban_ok, True, []),
           "date valide": (date_ok, True, []), "date impossible": (date_ok, False, [])}
    PAN = re.compile(r"`(\d[\d ]{12,21})`")

    for line in text.split(NL):
        h = line.strip()
        if h.startswith("**Valid test PANs") or (h.startswith("- `") and "·" in h):
            out["Luhn valide"][2].extend(PAN.findall(h))
        elif h.startswith("**Invalid (Luhn-fails):**"):
            out["Luhn invalide"][2].extend(PAN.findall(h))
        elif h.startswith("**Valid example:**"):
            m = re.search(r"`([A-Z]{2}[0-9A-Z ]{10,})`", h)
            if m:
                out["IBAN valide"][2].append(m.group(1))
        elif h.startswith("**Edge cases to generate:**"):
            # Le panier est une annotation en clair APRES la valeur, et sa forme varie :
            #   `2024-02-29` (leap, valid)        -> entre parentheses
            #   (`2023-04-31` invalid)            -> hors parentheses, la valeur etant DANS
            #                                        la parenthese d'un autre propos
            # Une premiere version exigeait la parenthese et perdait silencieusement le
            # troisieme cas. On lit donc les ~40 caracteres qui suivent, jusqu'a la valeur
            # suivante, et on refuse de classer si aucun des deux mots n'apparait.
            for m in re.finditer(r"`(\d{4}-\d{2}-\d{2}|\d{4}-\d{3})`", h):
                value = m.group(1)
                tail = h[m.end():m.end() + 40].split("`")[0].lower()
                if "invalid" in tail or "non-leap" in tail:
                    out["date impossible"][2].append(value)
                elif "valid" in tail:
                    out["date valide"][2].append(value)
                # sans annotation lisible : la ligne ne classe pas, on ne devine pas
    return out


ORACLES = os.path.join("eval", "oracles-2026-08-09")


def parse_iso_claims(text):
    """Lit les affirmations ISO DEPUIS library.md.

    Elles etaient codees en dur ici, et le controle verifiait donc **ses propres constantes** :
    remplacer `JP` par `ZZ` dans la bibliotheque passait sans un mot, tout comme changer l'unite
    mineure de BHD. Deux fautes injectees acceptees sur six -- exactement le defaut que
    `check_skill_counts` avait deja corrige un etage plus bas. Une affirmation doit etre lue la
    ou elle est ecrite, sinon le controle garde une copie et non l'original.
    """
    claims = {"alpha2": [], "alpha3": [], "minor_units": []}

    def codes(segment, n=None):
        """Les codes cites, hors parentheses -- « `UK` (it's `GB`) » affirme UK, pas GB."""
        segment = re.sub(r"\([^)]*\)", " ", segment)
        found = re.findall(r"`([A-Za-z]{1,3})`", segment)
        return [c for c in found if n is None or len(c) == n]

    for line in text.split(NL):
        h = line.strip()
        if h.startswith("**Valid alpha-2:**"):
            # Trois segments sur une seule ligne : valides alpha-2, valides alpha-3, invalides.
            # Les decouper explicitement, sinon les alpha-3 tombent dans le lot alpha-2 -- ce
            # qu'une premiere version faisait, en reprochant a `FRA` de ne pas etre un alpha-2.
            m = re.match(r"\*\*Valid alpha-2:\*\*(.*?)"
                         r"(?:\*\*Valid alpha-3:\*\*(.*?))?"
                         r"(?:\*\*Invalid:\*\*(.*))?$", h)
            if m:
                v2, v3, inv = (m.group(i) or "" for i in (1, 2, 3))
                claims["alpha2"] += [(c, True) for c in codes(v2, 2)]
                claims["alpha3"] += [(c, True) for c in codes(v3, 3)]
                claims["alpha2"] += [(c, False) for c in codes(inv, 2)]
        if "minor units" in h:
            claims["minor_units"] += [(c, u) for c, u in
                                      re.findall(r"`([A-Z]{3})`\s*\((\d)\s*minor units?\)", h)]
    return claims

NOT_COVERED = [
    ("RFC 9110", "semantique d'un code de statut : pas calculable, pas tabulable"),
    ("ISO 4217 / XXX", "le registre gele est indexe PAR PAYS -- l'absence de XXX n'y prouve rien, "
                       "et XXX est bel et bien assigne par la norme"),
    ("RFC 5322 / cas absents", "une adresse que le corpus canonique ne contient pas n'est ni "
                               "confirmee ni infirmee : elle est laissee ouverte, jamais supposee"),
]


def main():
    if not os.path.isfile(LIB):
        print("BROKEN: %s introuvable -- lancer depuis la racine du depot." % LIB)
        return 2
    text = io.open(LIB, encoding="utf-8").read()

    bad, checked = [], 0
    # Les paniers viennent du FICHIER. `CLAIMS` ne sert plus qu'a exiger qu'aucune section ne
    # disparaisse : une bibliotheque videe de sa section Luhn ne doit pas passer pour saine.
    parsed = parse_computable_claims(text)
    for label, (fn, expected, values) in parsed.items():
        if not values:
            bad.append((label, "-", "aucune valeur lue dans library.md -- section absente ou "
                                    "illisible, le controle porterait sur du vide"))
            continue
        for v in values:
            got = fn(v)
            checked += 1
            if got is not expected:
                bad.append((label, v, "la bibliotheque l'affirme %s ; le calcul dit %s"
                            % ("valide" if expected else "invalide",
                               "valide" if got else "invalide")))

    # --- registres externes geles ---------------------------------------------------------
    iso_path = os.path.join(ORACLES, "iso-3166-4217.json")
    mail_path = os.path.join(ORACLES, "rfc5322-isemail.json")
    external, unsettled = 0, []

    if os.path.isfile(iso_path):
        import json
        iso = json.load(io.open(iso_path, encoding="utf-8"))
        ISO_CLAIMS = parse_iso_claims(text)
        for key in ("alpha2", "alpha3", "minor_units"):
            if not ISO_CLAIMS[key]:
                bad.append(("ISO " + key, "-", "aucune affirmation lue dans library.md -- "
                            "le controle porterait sur du vide"))
        for code, claimed in ISO_CLAIMS["alpha2"]:
            external += 1
            if (code in iso["alpha2"]) is not claimed:
                bad.append(("ISO 3166 alpha-2", code, "la bibliotheque l'affirme %s ; le registre "
                            "dit le contraire" % ("valide" if claimed else "invalide")))
        for code, claimed in ISO_CLAIMS["alpha3"]:
            external += 1
            if (code in iso["alpha3"]) is not claimed:
                bad.append(("ISO 3166 alpha-3", code, "desaccord avec le registre"))
        for code, unit in ISO_CLAIMS["minor_units"]:
            external += 1
            real = iso["currency_minor_units"].get(code)
            if real != unit:
                bad.append(("ISO 4217 unite mineure", code,
                            "la bibliotheque dit %s ; le registre dit %s" % (unit, real)))
    else:
        unsettled.append("registre ISO absent de %s -- ISO 3166/4217 NON verifies" % ORACLES)

    if os.path.isfile(mail_path):
        import json
        corpus = {c["address"]: c for c in
                  json.load(io.open(mail_path, encoding="utf-8"))["cases"]}
        # Seules les adresses PRESENTES dans le corpus sont tranchees. Une absence n'est pas un
        # accord : elle est listee comme non tranchee.
        # La bibliotheque a TROIS paniers, pas deux : valide, invalide, et « valide mais
        # couramment refuse » (partie locale entre guillemets, syntaxe obsolete) qui doit rester
        # `[open]`. Une premiere version lisait le dernier en-tete rencontre avant l'adresse et
        # rangeait donc le troisieme panier dans « invalide » -- elle reprochait a la
        # bibliotheque exactement la nuance qu'on venait d'y ajouter. Seules les adresses citees
        # SUR une ligne d'en-tete sont donc tranchees.
        claims = {}
        for line in text.split(NL):
            head = line.strip()
            if head.startswith("**Valid:**"):
                for a in re.findall(r"`([^`]+@[^`]*)`", head):
                    claims[a] = True
            elif head.startswith("**Invalid:**"):
                for a in re.findall(r"`([^`]+@[^`]*)`", head):
                    claims[a] = False

        for addr, claimed in sorted(claims.items()):
            case = corpus.get(addr)
            if case is None:
                continue
            external += 1
            valid = not case["category"].startswith("ISEMAIL_ERR")
            if valid is not claimed:
                bad.append(("RFC 5322", addr, "la bibliotheque l'affirme %s ; le corpus canonique "
                            "le classe %s (%s)" % ("valide" if claimed else "invalide",
                                                   case["category"], case["diagnosis"])))
    else:
        unsettled.append("corpus RFC 5322 absent de %s -- emails NON verifies" % ORACLES)

    if bad:
        print("ORACLE FAUX -- une valeur attendue derivee d'ici serait erronee.\n")
        for label, value, why in bad:
            print("  %-18s %-38s %s" % (label, value, why))
        print("\nUne erreur dans un oracle emprunte l'autorite d'une norme : personne ne la")
        print("rediscutera dans le cahier genere. Corriger la bibliotheque, jamais le controle.")
        return 1

    print("OK: %d affirmation(s) calculee(s) (Luhn, IBAN mod-97, calendrier) + %d confrontee(s) "
          "aux registres externes geles." % (checked, external))
    for u in unsettled:
        print("  ATTENTION: %s" % u)
    print("\nNON couvert par ce controle, et volontairement dit tout haut :")
    for std, why in NOT_COVERED:
        print("  %-24s %s" % (std, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
