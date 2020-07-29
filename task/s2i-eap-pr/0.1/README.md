# Java EAP Source-to-Image (PipelineResource)

This task can be used for building `Java EAP` apps as reproducible Docker
images using Source-to-Image. [Source-to-Image (S2I)](https://github.com/openshift/source-to-image) is a toolkit and a workflow for building reproducible container images from source code. This java eap task uses `registry.redhat.io/jboss-eap-7-tech-preview/eap-cd-openshift-rhel8` builder image.

This current version of the Java EAP S2I builder image supports OpenJDK 11, EAP CD 18, and Maven 3.5.4-5.

## Installing the Java EAP Task

```
kubectl apply -f https://raw.githubusercontent.com/openshift/pipelines-catalog/master/task/s2i-eap-pr/0.1/s2i-eap-pr.yaml
```

## Parameters

* **PATH_CONTEXT**: Source path from where S2I command needs to be run
  (_default: `.`_)
* **TLSVERIFY**: Verify the TLS on the registry endpoint (for push/pull to a non-TLS registry) (_default:_ `true`)

## Resources

### Inputs

* **source**: A `git`-type `PipelineResource` specifying the location of the source to build.

### Outputs

* **image**: An `image`-type `PipelineResource` specifying the image that should
  be built.

Example:
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: s2i-eap-configmap
data:
  env-file: |
    MAVEN_ARGS_APPEND=-Dcom.redhat.xpaas.repo.jbossorg
    GALLEON_PROVISION_DEFAULT_FAT_SERVER=true
```

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

As EAP requires terms acceptance, a secret is needed for pulling the s2i source image. Create a secret with an Red Hat account (if you don't have one, join the [Developer Program](https://developers.redhat.com/) or register for a [30-day Trial Subscription](https://access.redhat.com/products/red-hat-jboss-enterprise-application-platform/evaluation)) and link it to the pipeline ServiceAccount.

```
oc create secret docker-registry <pull_secret_name> \
    --docker-server=registry.redhat.io \
    --docker-username=<user_name> \
    --docker-password=<password> \
    --docker-email=<optional>

oc secrets link pipeline <pull_secret_name>
```


## Creating the taskrun

This TaskRun runs the java EAP Task to fetch a Git repository and builds and pushes a container image using S2I and a Java EAP builder image. It is an example based on an existing BuildConfig of EAP:

```
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  name: s2i-eap-pr-taskrun
spec:
  # Use service account with git and image repo credentials
  serviceAccountName: pipeline
  taskRef:
    name: s2i-eap-pr
  params:
  - name: PATH_CONTEXT
    value: kitchensink
  - name: TLSVERIFY
    value: 'false'
  resources:
    inputs:
    - name: source
      resourceSpec:
        type: git
        params:
        - name: url
          value: https://github.com/jboss-developer/jboss-eap-quickstarts
        - name: revision
          value: openshift
    outputs:
    - name: image
      resourceSpec:
        type: image
        params:
        - name: url
          value: image-registry.openshift-image-registry.svc:5000/my-namespace/my-image-name
```
