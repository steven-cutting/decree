#!/usr/bin/env bash
set -euo pipefail
DEB=$(find build/apt -maxdepth 1 -type f -name '*.deb' -print -quit)
if [[ -z "$DEB" ]]; then
  echo "No .deb package found in build/apt" >&2
  exit 1
fi
REPO_DIR=build/repo
DIST=stable

sudo apt-get update && sudo apt-get install -y reprepro gnupg
mkdir -p "$REPO_DIR/conf"
cp packaging/apt/conf/distributions "$REPO_DIR/conf/distributions"

echo "$GPG_PRIVATE_KEY" | base64 -d | gpg --batch --import
reprepro --basedir "$REPO_DIR" includedeb $DIST "$DEB"

git config user.name "github-actions"; git config user.email "actions@github.com"
git checkout --orphan gh-pages || git checkout gh-pages
rm -rf ./*
cp -r "$REPO_DIR"/* ./
touch .nojekyll
git add .
git commit -m "Publish apt repo"
git push -f origin gh-pages
