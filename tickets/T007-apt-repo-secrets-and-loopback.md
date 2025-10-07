# T007 — APT repo: secrets + loopback signing

**user story & rationale**  
As a Debian/Ubuntu user, I want a signed apt repo that installs `decree`.

**scope (in)**  
- Add GitHub secrets `APT_GPG_PRIVATE_KEY` (base64) and `APT_GPG_PASSPHRASE`.  
- Update `publish_repo.sh` to import with `--pinentry-mode loopback` and passphrase.  
- Run `apt.yml` and publish to `gh-pages`.  
- Validate install in CI (container) from the published repo.

**non-goals (out)**  
- Distro submission.

**acceptance criteria**  
- Repo appears on `gh-pages`; CI job installs `decree` via `apt` and runs `decree --help`.

**test notes**  
- Add an ubuntu job that `echo "deb ... gh-pages URL ..." | sudo tee ...` then `apt-get update && apt-get install decree`.

**docs impact**  
- README: apt install instructions (key add + source line).

**dependencies**  
- T005 (wheel to build deb), optional.

**estimate**  
- L (1.5 days)

**labels**  
- area/dist, ci/release, quality/compliance, priority/p0
