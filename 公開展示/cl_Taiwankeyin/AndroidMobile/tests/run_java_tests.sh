#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/build-java-tests"
javac -encoding UTF-8 -d "$ROOT/build-java-tests" \
 "$ROOT/app/src/main/java/tw/cell/taiwankeyin/core/KeyinCore.java" \
 "$ROOT/tests/KeyinCoreTest.java"
java -cp "$ROOT/build-java-tests" KeyinCoreTest "$ROOT/app/src/main/assets/seed_zhuyin_tw.tsv"
