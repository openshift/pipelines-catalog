# .NET Core 2 Source-to-Image

This task can be used for building `.NET Core 2` apps as reproducible Docker
images using Source-to-Image. [Source-to-Image (S2I)](https://github.com/openshift/source-to-image)
is a toolkit and a workflow for building reproducible container images
from source code. This tasks uses the s2i-dotnet image build from [redhat-developer/s2i-dotnetcore](https://github.com/redhat-developer/s2i-dotnetcore).

.NET Core versions currently provided are:

- 2.1 (RHEL 7, RHEL 8, CentOS 7)
- 2.2 (RHEL 7, CentOS 7)

## Installing the .NET Core 2 Task

```
kubectl apply -f https://raw.githubusercontent.com/openshift/pipelines-catalog/master/task/s2i-dotnet-2/0.1/s2i-dotnet-2.yaml
```

## Parameters

* **MINOR_VERSION**: Minor version of the .NET Core 2
  (_default: 2_)
* **PATH_CONTEXT**: Source path from where S2I command needs to be run
  (_default: ._)
* **TLSVERIFY**: Verify the TLS on the registry endpoint (for push/pull to a
  non-TLS registry) (_default:_ `true`)
* **IMAGE**: Location of the repo where image has to be pushed.

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
  name: s2i-dotnet-2-pipeline
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
        name: s2i-dotnet-2
      workspaces:
        - name: source
          workspace: shared-workspace
      params:
        - name: IMAGE
          value: $(params.IMAGE)
```

## Creating the pipelinerun

This PipelineRun runs the .NET Core 2 Task to fetch a Git repository and builds and
pushes a container image using S2I and a .NET Core 2 builder image.

```yaml
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  name: s2i-dotnet-2-pipelinerun
spec:
  # Use service account with git and image repo credentials
  serviceAccountName: pipeline
  pipelineRunRef:
    name: s2i-dotnet-2-pipeline
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
