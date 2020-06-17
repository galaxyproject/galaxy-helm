#!/bin/sh

GIT_BRANCH=${GIT_BRANCH:-master}

git remote -v
git pull
if test $(git diff --name-status origin/"${GIT_BRANCH}" | grep -c "${CHART_NAME}/Chart.yml") = 0 ; then
    echo "Extracting label information"
    bump=$(python .github/scripts/extract_label.py)
    if [ ! "$bump" = "nobump" ]; then
        echo "Bumping version"
        bump2version --current-version ${bump} ./${CHART_NAME}/Chart.yaml
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add .
        git commit -m "Automatic Version Bumping"

        REPOSITORY=${INPUT_REPOSITORY:-$GITHUB_REPOSITORY}
        REMOTE="https://${GITHUB_ACTOR}:${GIT_TOKEN}@github.com/${REPOSITORY}.git"

        echo "Push to branch $GIT_BRANCH";
        [ -z "${GIT_TOKEN}" ] && {
            echo 'Missing input "GIT_TOKEN: ${{ secrets.GITHUB_TOKEN }}".';
            exit 1;
        };

        git push "${REMOTE}" HEAD:${GIT_BRANCH} -v -v
    fi
fi