# CELL TaiwanKeyin — Zhuyin Traditional / Pinyin Simplified acceptance

## Source and scope
- Branch: `feature/taiwankeyin-pinyin-toggle-20261109`
- Retain unchanged production `main` and permanent package `tw.cell.taiwankeyin`.
- Android IME: `TaiwanKeyinImeService`, state in `keyboard_settings/pinyin_mode`.
- Zhuyin baseline is the existing 158,905-row offline Taiwanese dictionary; PinyinComposer resolves Hanyu Pinyin into Zhuyin readings, and queries this existing index.
- Simplified UI candidates and committed text are converted with Android ICU `Traditional-Simplified`. This is NOT an independently ranked Simplified Chinese lexicon, and is NOT OpenCC phrase-level parity.
- Production `app-release-unsigned.apk` and sidecar `app-sidecar-unsigned.apk` remain unsigned and require private signing. The new, isolated `pinyinTest` variant builds with Android debug signing under `tw.cell.taiwankeyin.pinyintest`; it is intended only for functional testing, never for production updates.

## Reproducible checks
1. JVM: run `bash tests/run_java_tests.sh` from project, validating pinyin syllables, continuous `nihao` composition, backspace and mode-clear.
2. Android: build `gradle :app:assembleDebug :app:assembleRelease :app:assembleSidecar :app:assemblePinyinTest` after staging full lexicon.
3. Install the debug-signed `app-pinyinTest.apk` on Android API 26+, enable its isolated IME and switch to it; use the `CELL-TaiwanKeyin-Zhuyin-Pinyin-pilot-signed-debug` Actions artifact.
4. Tap 注繁/拼簡 on Zhuyin punctuation/palette row; verify keyboard switches to QWERTY Pinyin and displays 拼簡/注繁 toggle. Restart keyboard and verify persisted Pinyin choice.
5. Enter `nihao`; verify 你好 in candidates, choose it, and check text is committed once.
6. Enter `zhongguo`; verify 中国 is a possible simplified candidate. Do not assert exact rank until measured on device.
7. Test `yin`, `ying`, `yue`, `xue`, `yuan`, `wen`; verify no raw letters are committed by pressing Space when there are no candidates.
8. Switch to English, then Chinese, symbols, and back; verify no stale preedit, accidental commit, duplicate insertion or keyboard crash.
9. In password field: confirm learning is disabled. Test backspace and clipboard paste in both Chinese modes.
10. Confirm original app remains installed and its SQLite learning data untouched.

## Blocking gaps before release promotion
- Need device-level UX and input acceptance tests: JVM and CI Android builds cannot establish actual touchscreen usability.
- Need independent Simplified lexicon, phrase-aware OpenCC conversion and ranking parity for production-quality 拼簡. Current ICU conversion is a preliminary adapter; conversion may be context-sensitive and requires validation.
- CI does not sign permanent-package release APK. Only the isolated debug-signed pilot should be installed for testing; its signing certificate can differ across runs.
- No merge to production before confirming the above.
