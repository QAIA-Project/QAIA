# Trou de DevEx confirme le 2026-08-08 : ni Makefile, ni Dockerfile, ni devcontainer dans le
# depot. C'est le seul point sur lequel l'analyse externe de Gemini tapait juste, et il ne coute
# rien a combler. Les cibles ci-dessous sont celles qu'un nouveau venu cherche en premier.
.PHONY: help setup check demo demo-stop lint test clean

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Installe les dependances de la demo et de ses tests
	cd examples/expense-demo/tests && npm install

check: ## Lance tous les controles que la CI lance (skills, provenance, outillage)
	python eval/tools/lint_skills.py
	python eval/tools/check_skill_counts.py
	python eval/tools/check_decision_register.py
	python eval/tools/check_open_work_issue.py
	python eval/tools/selfcheck_open_work_issue.py
	python eval/tools/check_schema_matches_validator.py
	python eval/tools/check_requirement_drift.py
	python eval/tools/check_published_copies.py
	python eval/tools/selfcheck_automation_score.py
	python eval/tools/selfcheck_spec_suite_drift.py
	python eval/tools/check_loop_wiring.py
	python eval/tools/check_oracle_library.py
	python eval/tools/check_agents_tier.py
	python eval/tools/check_retired_framing.py
	python eval/tools/selfcheck_markdown_shell_hook.py
	python eval/tools/selfcheck_gherkin_dialect.py
	python eval/tools/selfcheck_rule3.py
	python eval/tools/check_test_levels.py
	python eval/tools/selfcheck_test_levels.py
	python eval/tools/check_nl_projection.py
	python eval/tools/selfcheck_nl_projection.py
	python eval/tools/selfcheck_manifest_bylevel.py
	# La CI balaie `find plugins eval -name 'manifest*.json'` ; il n'existe aucun
	# manifest*.json sous `plugins/`, donc les deux perimetres sont equivalents en pratique.
	# J'y avais ajoute `--batch plugins` « pour qu'ils le restent » : l'outil sort 2 sur un
	# ensemble vide et la CI est passee au rouge. Je l'avais cru inoffensif parce que j'avais
	# lu `$?` APRES un pipe -- donc le code de `tail`, pas celui de l'outil.
	# Le balayage disait `eval` seul. Les DEUX manifestes en contrat 1.1 -- ceux qui prouvent
	# le chantier `design.byLevel` -- vivent sous `examples/` et `site-qa/`, donc hors du
	# validateur ecrit pour eux (releve le 2026-08-11 par une relecture hostile, troisieme
	# faute de perimetre du meme jour). Le balayage part desormais de la racine.
	python eval/tools/validate_manifest.py --batch .
	# Ce qui suit manquait vraiment : la cible se disait « tous les controles que la CI lance »
	# et en omettait la moitie. Un nouveau venu la voyait verte, poussait, et decouvrait la CI
	# rouge -- ce qui est pire que pas de cible du tout.
	# Les trois portes de structure -- sources du marketplace relatives, rien d'executable sous
	# plugins/, contrat de sortie identique partout -- etaient ecrites en shell dans ci.yml
	# seulement. Les recopier ici en aurait fait une deuxieme copie a maintenir, la faute meme
	# qu'on venait de corriger sur le perimetre Gherkin. Un script, appele des deux endroits.
	python eval/tools/check_universal_default.py
	python eval/tools/check_skill_cli_claims.py
	python eval/tools/check_repo_structure.py
	@echo "--- tests du pont MCP ---"
	@cd mcp-bridge && npm ci --no-audit --no-fund --silent && npm test
	$(MAKE) lint

# Meme reference que `tests/playwright.config.js`. Sans elle, l'application et sa suite lisent
# deux horloges differentes et cinq tests deviennent rouges a une date que personne n'a decidee.
DEMO_NOW ?= 2026-07-26

demo: ## Demarre l'application de demonstration sur http://localhost:4500
	@echo "ExpenseFlow sur http://localhost:4500 (horloge figee au $(DEMO_NOW)) -- Ctrl+C pour arreter"
	DEMO_NOW=$(DEMO_NOW) node examples/expense-demo/app/server.js

test: ## Joue la suite generee contre la demo (la demo doit tourner)
	cd examples/expense-demo/tests && npx playwright test

# Le linter vient de `package-lock.json`, pas de `npx --yes` : la decision T15 epingle chaque
# Action par SHA, et le seul paquet npm que la CI executait etait telecharge au vol -- version
# fixee, octets libres. `npm ci` verifie l'empreinte d'integrite avant d'executer (B35).
#
# Seule definition du perimetre Gherkin du depot. La CI appelle cette cible plutot que de
# reecrire la liste : elle existait en double, les deux copies ont diverge, et `make lint` etait
# rouge sur tout clone propre pendant que la CI etait verte. Meme classe que la panne du
# 2026-07-30 consignee dans CLAUDE.md -- une liste dupliquee finit toujours par diverger.
FEATURE_EXCLUDES = -not -path './node_modules/*' -not -path '*/export/*' \
	  -not -path './eval/concerns-zone-fixtures/*' -not -path './eval/gold-set/*' \
	  -not -path './eval/goldset-hardened/*' -not -path './eval/baselines/*' \
	  -not -path './eval/gherkin-conformance/*' \
	  -not -path './eval/portability-2026-08-08/*' \
	  -not -path './eval/portability-2026-08-09/*'

# `find ... | grep -q .` masquait le code de sortie de find derriere celui de grep. Un perimetre
# casse -- il a suffi d'un backslash-n litteral dans FEATURE_EXCLUDES -- faisait echouer find,
# qui ne rendait rien, donc grep echouait, donc la branche `else` annoncait « rien a verifier »
# et la cible sortait VERTE sans avoir lint un seul fichier. C'est mot pour mot la panne
# fondatrice de CLAUDE.md (« le job Lint Gherkin etait casse en silence »), revenue dans le
# mecanisme bati pour l'empecher -- et c'est la branche serviable qui convertissait l'erreur en
# vert. Le code de sortie de find est desormais lu, et zero fichier trouve est une ERREUR : ce
# depot contient des .feature, donc un perimetre qui n'en voit aucun est casse (2026-08-10).
# La cible ANNONCE combien de fichiers elle verifie : une cible muette qui passe est
# indistinguable d'une cible qui n'a rien fait -- c'est ce silence qui a laisse la panne
# de perimetre invisible. Le nombre est la preuve, dans le log, que le linter a mordu.
lint: ## Verifie les cahiers Gherkin comme le fait la CI
	@test -d node_modules/gherkin-lint || npm ci --no-audit --no-fund --silent
	@files=$$(find . -name '*.feature' $(FEATURE_EXCLUDES)) || { \
	  echo "ERREUR : perimetre Gherkin casse -- find a echoue." ; exit 1 ; } ; \
	  if [ -z "$$files" ]; then \
	    echo "ERREUR : aucun .feature trouve alors que ce depot en contient." ; exit 1 ; \
	  fi ; \
	  echo "Perimetre Gherkin : $$(echo "$$files" | wc -l) fichier(s) a verifier." ; \
	  echo "$$files" | xargs ./node_modules/.bin/gherkin-lint -c .gherkin-lintrc

clean: ## Supprime les sorties de test
	rm -rf examples/*/tests/test-results examples/*/tests/results.json
