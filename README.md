# ⚠️ ⚠ ️⚠️ Warning ⚠️ ⚠️ ⚠️

This repository is deprecated.

🧑‍💻 Development and maitenence of these tasks have moved to:
https://github.com/tektoncd/operator/tree/main/cmd/openshift/operator/kodata/tekton-addon/addons/02-clustertasks/source_local

The tasks in this repository are not maintained anymore.

--- 

# Pipelines Catalog

This repository contains a catalog of Tekton `Task` resources (and
someday `Pipeline`s and `Resource`s), which are designed to be
reusable in many pipelines.

Each `Task` is provided in a separate directory along with a README.md and a
Kubernetes manifest, so you can choose which `Task`s to install on your
cluster.

This is an OpenShift-specific Tekton catalog, which follows the same
rules and patterns as
[`tektoncd/catalog`](https://github.com/tektoncd/catalog).
