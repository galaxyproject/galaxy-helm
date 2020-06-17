#!/bin/bash

[ -z "${GIT_TOKEN}" ] && {
    echo 'Missing input "GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}".';
    exit 1;
};
[ -z "${CHARTS_REPO}" ] && {
    echo 'Missing input "CHARTS_REPO: cloudve/helm-charts".';
    exit 1;
};

set -e

BRANCH=${CHARTS_BRANCH:-master}
CHARTS_DIR=$(basename $CHARTS_REPO)
REMOTE="https://${GITHUB_ACTOR}:${GIT_TOKEN}@github.com/${CHARTS_REPO}.git"

echo "Pushing to branch $BRANCH of repo $CHARTS_REPO";

cd "${CHART_NAME}" && rm -rf charts && rm -f requirements.lock && helm dependency update && cd ..
git clone "${REMOTE}" && cd "${CHARTS_DIR}" && git checkout $BRANCH && cd ..
CHARTS_ABS_DIR=$(realpath $CHARTS_DIR)
cd "${CHART_NAME}" && sh scripts/helm_package "${CHARTS_ABS_DIR}/charts" && cd ..
cd "${CHARTS_DIR}" && helm repo index . --url "https://raw.githubusercontent.com/${CHARTS_REPO}/${BRANCH}/"
git config --local user.email "action@github.com"
git config --local user.name "GitHub Action"
git add . && git commit -m "Automatic Packaging of ${CHART_NAME} chart" 
git push "${REMOTE}" HEAD:${BRANCH};
