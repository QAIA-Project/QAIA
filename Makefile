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
	python eval/tools/validate_manifest.py --batch eval

demo: ## Demarre l'application de demonstration sur http://localhost:4500
	@echo "ExpenseFlow sur http://localhost:4500 -- Ctrl+C pour arreter"
	node examples/expense-demo/app/server.js

test: ## Joue la suite generee contre la demo (la demo doit tourner)
	cd examples/expense-demo/tests && npx playwright test

lint: ## Verifie les cahiers Gherkin comme le fait la CI
	find . -name '*.feature' -not -path './node_modules/*' -not -path '*/export/*' \
	  -not -path './eval/concerns-zone-fixtures/*' -not -path './eval/gold-set/*' \
	  -not -path './eval/goldset-hardened/*' -not -path './eval/baselines/*' \
	  -exec npx --yes gherkin-lint@4.2.4 -c .gherkin-lintrc {} +

clean: ## Supprime les sorties de test
	rm -rf examples/*/tests/test-results examples/*/tests/results.json
