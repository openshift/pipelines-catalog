#!/usr/bin/env bash

# Synchs the release-next branch to master and then triggers CI
# Usage: update-to-head.sh

set -e
set -x
REPO_NAME=`basename $(git remote get-url origin)`
BRANCH=${BRANCH:-master}
LABEL=nightly-ci

# Reset release-next to upstream/master.
git fetch origin ${BRANCH}
git checkout origin/${BRANCH} --no-track -B release-next

git push -f origin HEAD:release-next

# Trigger CI
git checkout release-next --no-track -B release-next-ci
date > ci
git add ci
git commit -m "Tekton as a code triggered CI on branch 'release-next' after synching to upstream/master"

git push -f origin HEAD:release-next-ci

already_open_github_issue_id=$(hub pr list -s open -f "%I %l%n"|grep ${LABEL}| awk '{print $1}'|head -1)
[[ -n ${already_open_github_issue_id} ]]  && {
    echo "PR for nightly is already open on #${already_open_github_issue_id} sending a /retest"
    hub api repos/openshift/${REPO_NAME}/issues/${already_open_github_issue_id}/comments -f body='/retest'
    exit
}

hub pull-request -m "🛑🔥 Triggering Nightly CI for ${REPO_NAME} 🔥🛑" -m "/hold" -m "Nightly CI do not merge :stop_sign:" \
    --no-edit -l "${LABEL}" -b openshift/${REPO_NAME}:release-next -h openshift/${REPO_NAME}:release-next-ci
