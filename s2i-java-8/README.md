# Java 8 Source-to-Image

This task can be used for building `Java 8` apps as reproducible Docker 
images using Source-to-Image. [Source-to-Image (S2I)](https://github.com/openshift/source-to-image)
is a toolkit and a workflow for building reproducible container images
from source code. This java 8 task uses `registry.access.redhat.com/redhat-openjdk-18/openjdk18-openshift` builder image

The current version of the Java S2I builder image supports OpenJDK 1.8, Jolokia 1.3.5, and Maven 3.3.9-2.8

## Installing the Java 8 Task

```
kubectl apply -f https://raw.githubusercontent.com/openshift/pipelines-catalog/master/s2i-java-8/s2i-java-8-task.yaml
```

## Inputs

### Parameters

* **PATH_CONTEXT**: Source path from where S2I command needs to be run
  (_default: `.`_)
* **TLSVERIFY**: Verify the TLS on the registry endpoint (for push/pull to a
  non-TLS registry) (_default:_ `true`)
* **MAVEN_CLEAR_REPO**: Remove the Maven repository after the artifact is 
  built (_default:_ `false`)
* **MAVEN_ARGS_APPEND**: Additional Maven arguments (_default:_ `Empty String`)
* **MAVEN_MIRROR_URL**: The base URL of a mirror used for retrieving artifacts 
  (_default:_ `http://repo.maven.apache.org/maven2`)


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

This TaskRun runs the java 8 Task to fetch a Git repository and builds and 
pushes a container image using S2I and a Java 8 builder image.

```
apiVersion: tekton.dev/v1alpha1
kind: TaskRun
metadata:
  name: s2i-java8-taskrun
spec:
  # Use service account with git and image repo credentials
  serviceAccount: pipeline
  taskRef:
    name: s2i-java-8
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