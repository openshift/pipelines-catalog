PIPELINE_OUTPUT_FILE := .tekton/pipeline.yaml
TEMPLATE_FILE := openshift/gen/pipeline.django.yaml
PRESTEP_FILE := openshift/gen/prestep.yaml

all: yamlcheck generate

generate:
	./openshift/gen/generate-pipeline-catalog.py task/ $(TEMPLATE_FILE) $(PRESTEP_FILE) > $(PIPELINE_OUTPUT_FILE)
.PHONY: generate

yamlcheck:
	yamllint -c ~/.yamllint task

check:
	@make generate PIPELINE_OUTPUT_FILE=/tmp/pipeline-check.yaml
	@diff -u $(PIPELINE_OUTPUT_FILE) /tmp/pipeline-check.yaml || exit 1
