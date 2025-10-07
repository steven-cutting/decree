# APT Packaging

This directory contains scripts to build a .deb from the PyPI wheel and publish
a signed apt repo using reprepro on GitHub Pages.

* build: run `packaging/apt/scripts/build_deb.sh` after building wheels (keep
  `dist/` present)
* publish: set secrets `APT_GPG_PRIVATE_KEY` (base64) and `APT_GPG_PASSPHRASE`,
  then run `packaging/apt/scripts/publish_repo.sh`
