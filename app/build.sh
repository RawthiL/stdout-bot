#!/bin/bash
set -e

imageNAME="rawthil_stdout_bot"

# Get last commit hash and repo state
COMMIT_HASH=$(git log -n1 --format=format:"%H")
COMMIT_CLEAN=True
if [ -n "$(git status -s)" ];
then COMMIT_CLEAN=False
fi

echo "$COMMIT_HASH"
echo "$COMMIT_CLEAN"

# build image
docker build . -f Dockerfile --build-arg COMMIT_HASH="$COMMIT_HASH" --build-arg COMMIT_CLEAN="$COMMIT_CLEAN" -t "$imageNAME":latest

# Broadcast image name and tag
echo "$imageNAME"
echo "$imageTAG"