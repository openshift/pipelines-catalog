# Java 11 Source-to-Image

This task can be used for building `Java 11` apps as reproducible Docker
images using Source-to-Image. [Source-to-Image (S2I)](https://github.com/openshift/source-to-image)
is a toolkit and a workflow for building reproducible container images
from source code. This java 11 task uses `registry.access.redhat.com/openjdk/openjdk-11-rhel7` builder image

## Installing the Java 11 Task

```
kubectl apply -f https://raw.githubusercontent.com/openshift/pipelines-catalog/master/task/s2i-java-11/0.1/s2i-java-11.yaml
```

## Parameters

* **PATH_CONTEXT**: Source path from where S2I command needs to be run
  (_default: `.`_)
* **TLSVERIFY**: Verify the TLS on the registry endpoint (for push/pull to a
  non-TLS registry) (_default:_ `true`)
* **MAVEN_ARGS_APPEND**: Additional Maven arguments (_optional_, _no default_)
* **MAVEN_CLEAR_REPO**: Remove the Maven repository after the artifact is
  built (_default:_ `false`)
* **MAVEN_MIRROR_URL**: The base URL of a mirror used for retrieving artifacts
  ((_optional_, _no default_))

## Workspaces

* **source**: A workspace specifying the location of the source to
  build.

## Creating a ServiceAccount

S2I builds an image and pushes it to the destination registry which is
defined as a parameter. The image needs proper credentials to be
authenticated by the remote container registry. These credentials can
be provided through a serviceaccount. See [Authentication](https://github.com/tektoncd/pipeline/blob/master/docs/auth.md#basic-authentication-docker)
for further details.

If you run on OpenShift, you also need to allow the service
account to run privileged containers. Due to security considerations
OpenShift does not allow containers to run as privileged containers
by default.

Run the following in order to create a service account named
`pipelines` on OpenShift and allow it to run privileged containers:

```
oc create serviceaccount pipeline
oc adm policy add-scc-to-user privileged -z pipeline
oc adm policy add-role-to-user edit -z pipeline
```

## Using a a `Pipeline` with `git-clone`

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: s2i-java-11-pipeline
spec:
  params:
    - name: IMAGE
      description: Location of the repo where image has to be pushed
      type: string
  workspaces:
    - name: shared-workspace
  tasks:
    - name: fetch-repository
      taskRef:
        name: git-clone
      workspaces:
        - name: output
          workspace: shared-workspace
      params:
        - name: url
          value: https://github.com/username/reponame
        - name: subdirectory
          value: ""
        - name: deleteExisting
          value: "true"
    - name: s2i
      taskRef:
        name: s2i-java-11
      workspaces:
        - name: source
          workspace: shared-workspace
      params:
        - name: IMAGE
          value: $(params.IMAGE)
```

## Creating the pipelinerun

This PipelineRun runs the Java 11 Task to fetch a Git repository and builds and
pushes a container image using S2I and a Java 11 builder image.

```yaml
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  name: s2i-java-11-pipelinerun
spec:
  # Use service account with git and image repo credentials
  serviceAccountName: pipeline
  pipelineRunRef:
    name: s2i-java-11-pipeline
  params:
  - name: IMAGE
    value: quay.io/my-repo/my-image-name
  workspaces:
  - name: shared-data
    volumeClaimTemplate:
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
```
