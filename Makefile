PIPELINE_OUTPUT_FILE := .tekton/pipeline.yaml
TEMPLATE_FILE := openshift/gen/pipeline.django.yaml
PRESTEP_FILE := openshift/gen/prestep.yaml

all: yamlcheck generate

venv:
	@set -x;[ -d .venv/ ] || { python3 -mvenv .venv && ./.venv/bin/pip install -r requirements.txt || rm -rf .venv ;}
.PHONY: generate

generate: venv
	.venv/bin/python3 ./openshift/gen/generate-pipeline-catalog.py task/ $(TEMPLATE_FILE) $(PRESTEP_FILE) > $(PIPELINE_OUTPUT_FILE)
.PHONY: generate

yamlcheck:
	yamllint task

check:
	@make generate PIPELINE_OUTPUT_FILE=/tmp/pipeline-check.yaml
	@diff -u $(PIPELINE_OUTPUT_FILE) /tmp/pipeline-check.yaml || exit 1

# need a cluster check
apply-check: SHELL:=/bin/bash
apply-check:
	kubectl apply --dry-run=client -f <(sed -e 's,{{namespace}},pipelines-catalog,g' -e 's,{{repo_url}},https://github.com/openshift/pipelines-catalog,' -e 's,{{revision}},master,' .tekton/pipeline.yaml)
