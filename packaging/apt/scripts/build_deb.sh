#!/usr/bin/env bash
set -euo pipefail
VER=$(python -c 'import tomllib,sys; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')
WHL=$(ls dist/decree-*.whl | head -n1)
mkdir -p build/apt
fpm -s python -t deb "$WHL" \
--name decree \
--version "$VER" \
--maintainer "Steven Cutting" \
--description "Decree: Python adr-tools" \
--license "BSD-3-Clause" \
--no-auto-depends \
--depends "python3 (>=3.11)" \
--package "build/apt/decree_${VER}*all.deb"
echo "Built build/apt/decree*${VER}_all.deb"
