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
