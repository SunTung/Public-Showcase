# cl_Taiwankeyin — R2 Zhuyin composition and candidate engine

**R2 engineering prototype, not a Windows TSF IME.** This preserves R1 as an unchanged sibling source directory.

## Build/test

From a checkout containing `R1_CppCore/` and `R2_Zhuyin/` as siblings:

```sh
cmake -S R2_Zhuyin -B build-r2 -DCMAKE_BUILD_TYPE=Release
cmake --build build-r2 --parallel
ctest --test-dir build-r2 --output-on-failure
./build-r2/cellkeyin_r2_cli R2_Zhuyin/data/seed_zhuyin_tw.tsv :memory:
```

`R2_Zhuyin/CMakeLists.txt` can also be built standalone when `CELLKEYIN_R1_ROOT` points to the verified R1 sources. Requires C++17, ICU uc+i18n, SQLite3.

## Headless session behavior

- Complete **37-symbol Dachen** phonetic map plus five tones (`space`, `6`, `3`, `4`, `7`), matching Taiwan keyboard arrangement.
- Type a syllable, then its tone; candidates appear only when syllable boundary is explicitly completed.
- Continuing to type a new syllable after tone extends the uncommitted phrase. Candidate selection by `choose <1-based-index>` is the **only** event that commits/learns its converted text.
- `backspace` edits composing strokes or reopens a toned syllable; `escape` cancels with no learning.
- Committing a punctuation mark is an independent explicit operation only while idle. Committed brackets and colon preserve R1 experience-context; hard punctuation resets it.
- `:memory:` uses temporary SQLite; for persistence supply writable database filename; never publish user database.

### Example CLI input

```text
key s
key u
tone 3
choose 1
key c
key l
tone 3
choose 1
context
punct 。
context
```

### Deliberate limitations

1. The **seed dictionary is hand-authored and tiny**. It demonstrates single/compound lookup, homophones and adaptive ranking; it is not a full Mandarin pronunciation dictionary. Users can replace/extend the UTF-8 TSV dictionary via `Lexicon::load_tsv`.
2. The phonetic parser enforces the initial→medial→final order and lone initial restrictions, but **does not perform complete Mandarin syllable phonotactics**. Unknown/unsupported readings return an empty menu rather than fabricated Chinese characters.
3. R2 is a CLI/SDK, not a native Windows graphical frontend, installer or TSF DLL; Windows MSVC/Win11 tests remain pending R3/R4.
4. R1's original self-tests are built and executed unchanged as a regression target.
5. SQLite learning uses chosen output only, not raw preedit keystrokes; privacy controls are supplied by the host through existing R1 `Engine::set_sensitive`.

See `docs/R2_REPORT_20261108.md` for actual local verification results; the presence of tests alone is not evidence that a Windows IME works.
