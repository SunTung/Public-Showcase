# cl_Taiwankeyin — R1 cell memory kernel (C++17)

This is the **tested, headless R1 library**, not yet a Windows TSF input method nor `cl_Taiwankeyin.exe`.

Core: ICU Unicode grapheme segmentation, 10-effective-character sliding context, hard/soft punctuation rules, rolling n-gram phrase learning, SQLite WAL persistence, context-weighted reading candidate ranking and rejection feedback, sensitive mode and learning erase.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
./build/cellkeyin_r1_cli :memory:
```

Dependencies: C++17 compiler, CMake >= 3.20, ICU (uc+i18n), SQLite3. For Windows builds install ICU and SQLite using vcpkg or other compatible toolchain. `R1` has been verified only on the recorded Linux environment. All Windows TSF adapter, complete Zhuyin keyboard maps, dictionary and executable packaging are reserved for R2–R5.

To run CLI with a persistent database, pass a dedicated writable path. The CLI is a **test harness** and cannot inject text into other applications.

## Privacy and engineering limits

The rolling phrase store records up to ten **effective grapheme clusters**, but soft structural delimiters can be present in stored phrase text. Context relation keys are FNV-1a identifiers: **not encryption and not secrecy**; the persisted phrase text remains sensitive. Do not publish real user files. Secure-field classification must be supplied by a future Windows TSF adapter; the core only provides `set_sensitive(true)`.

SQLite is written on confirmed input only; composing keystrokes and unconfirmed candidates must never call `commit`. `rank()` is deterministic for the same saved counts and wall-clock recency baseline. Ranker weights are initial empirical values requiring later evaluation, not a verified accuracy improvement.

## Reference

[Project R0 specification](https://github.com/SunTung/Public-Showcase/blob/main/%E5%85%AC%E9%96%8B%E5%B1%95%E7%A4%BA/cl_Taiwankeyin/PLAN.md)
