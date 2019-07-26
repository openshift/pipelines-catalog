# Python 3 Source-to-Image

This task can be used for building `Python` apps as reproducible Docker 
images using Source-to-Image. [Source-to-Image (S2I)](https://github.com/openshift/source-to-image)
is a toolkit and a workflow for building reproducible container images
from source code. This tasks uses the s2i-python image build from [sclorg/s2i-python-container](https://github.com/sclorg/s2i-python-container).

Python 3 versions currently provided are:

- Python 3.5
- Python 3.6

## Installing the Python Task

```
kubectl apply -f https://raw.githubusercontent.com/openshift/pipelines-catalog/master/s2i-python-3/s2i-python-3-task.yaml
```

## Inputs

### Parameters

* **MINOR_VERSION**: Minor version of the Python 3
  (_default: 6_)
* **PATH_CONTEXT**: Source path from where S2I command needs to be run
  (_default: ._)
* **TLSVERIFY**: Verify the TLS on the registry endpoint (for push/pull to a
  non-TLS registry) (_default:_ `true`)


### Resources

* **source**: A `git`-type `PipelineResource` specifying the location of the
  source to build.

## Outputs

### Resources

* **image**: An `image`-type `PipelineResource` specifying the image that should
  be built.

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

## Creating the taskrun

This TaskRun runs the python 3 Task to fetch a Git repository and builds and 
pushes a container image using S2I and a python 3 builder image.

```
apiVersion: tekton.dev/v1alpha1
kind: TaskRun
metadata:
  name: s2i-python3-taskrun
spec:
  # Use service account with git and image repo credentials
  serviceAccount: pipeline
  taskRef:
    name: s2i-python-3
  inputs:
    resources:
    - name: source
      resourceSpec:
        type: git
        params:
        - name: url
          value: https://github.com/username/reponame
  outputs:
    resources:
    - name: image
      resourceSpec:
        type: image
        params:
        - name: url
          value: quay.io/my-repo/my-image-name
```