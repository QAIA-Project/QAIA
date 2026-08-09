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
	python eval/tools/check_schema_matches_validator.py
	python eval/tools/check_requirement_drift.py
	python eval/tools/check_published_copies.py
	python eval/tools/selfcheck_automation_score.py
	python eval/tools/selfcheck_spec_suite_drift.py
	python eval/tools/check_loop_wiring.py
	python eval/tools/check_oracle_library.py
	python eval/tools/check_agents_tier.py
	python eval/tools/selfcheck_rule3.py
	# La CI balaie `find plugins eval -name 'manifest*.json'` ; il n'existe aucun
	# manifest*.json sous `plugins/`, donc les deux perimetres sont equivalents en pratique.
	# J'y avais ajoute `--batch plugins` « pour qu'ils le restent » : l'outil sort 2 sur un
	# ensemble vide et la CI est passee au rouge. Je l'avais cru inoffensif parce que j'avais
	# lu `$?` APRES un pipe -- donc le code de `tail`, pas celui de l'outil.
	python eval/tools/validate_manifest.py --batch eval
	# Ce qui suit manquait vraiment : la cible se disait « tous les controles que la CI lance »
	# et en omettait la moitie. Un nouveau venu la voyait verte, poussait, et decouvrait la CI
	# rouge -- ce qui est pire que pas de cible du tout.
	# Les trois portes de structure -- sources du marketplace relatives, rien d'executable sous
	# plugins/, contrat de sortie identique partout -- etaient ecrites en shell dans ci.yml
	# seulement. Les recopier ici en aurait fait une deuxieme copie a maintenir, la faute meme
	# qu'on venait de corriger sur le perimetre Gherkin. Un script, appele des deux endroits.
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

# Seule definition du perimetre Gherkin du depot. La CI appelle cette cible plutot que de
# reecrire la liste : elle existait en double, les deux copies ont diverge, et `make lint` etait
# rouge sur tout clone propre pendant que la CI etait verte. Meme classe que la panne du
# 2026-07-30 consignee dans CLAUDE.md -- une liste dupliquee finit toujours par diverger.
FEATURE_EXCLUDES = -not -path './node_modules/*' -not -path '*/export/*' \
	  -not -path './eval/concerns-zone-fixtures/*' -not -path './eval/gold-set/*' \
	  -not -path './eval/goldset-hardened/*' -not -path './eval/baselines/*' \
	  -not -path './eval/portability-2026-08-08/*'

lint: ## Verifie les cahiers Gherkin comme le fait la CI
	@if find . -name '*.feature' $(FEATURE_EXCLUDES) | grep -q .; then \
	  find . -name '*.feature' $(FEATURE_EXCLUDES) \
	    -exec npx --yes gherkin-lint@4.2.4 -c .gherkin-lintrc {} + ; \
	else \
	  echo "Aucun fichier .feature dans le perimetre -- rien a verifier" ; \
	fi

clean: ## Supprime les sorties de test
	rm -rf examples/*/tests/test-results examples/*/tests/results.json
