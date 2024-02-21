#!/usr/bin/env bash

# Date since the last release.  We will search for commits newer than this.
# TODO There is probably some Git magic we could do to figure this out
SINCE=${SINCE:-2023-08-19}

# The last version that was tagged.
# TODO There is probably some Git magic we could do to figure this out
LATEST=${LATEST:-5.7.6}

# Search the git log for commits that did an Automatic version bump.
git log --oneline --grep=Automatic --since=$SINCE | awk '{print $1,$NF}' | grep -v $LATEST | tail -r | while read -r line ; do
	commit=$(echo $line | awk '{print $1}')
	tag=v$(echo $line | awk '{print $2}')
	# Get the actual date the commit was made
	export GIT_COMMITTER_DATE=$(git show --format=%aD $commit | head -1)
	# Tag the commit
	echo "Tagging $commit as $tag $GIT_COMMITTER_DATE"
	git checkout $commit
	git tag -a -m "Automatic tagging of $tag" $tag
	git push origin $tag
	# Generate the release.
	gh release create $tag --generate-notes --latest
done 
git checkout master
echo "Done."