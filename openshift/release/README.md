# Release creation

### Creating a branch based off an upstream release tag

To create a clean branch from an upstream release tag, use the `create-release-branch.sh` script:

```bash
$ ./openshift/release/create-release-branch.sh v0.4.1
```

This will create a new branch `release-0.4` based off the tag `v0.4.1` and push
the tag and release branch to origin.

If you have a `v0.4.2` release it will reset the `release-0.4` branch to it.
