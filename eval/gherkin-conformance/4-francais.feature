# language: fr
Fonctionnalité: Validation de posologie

  Contexte:
    Etant donné un médicament "DRUG-A" avec une dose maximale de 40 mg

  Scénario: une dose au-dessus du maximum est bloquée
    Quand le prescripteur saisit 41 mg
    Alors la validation renvoie "blocked"
    Et la prescription ne peut pas être signée
