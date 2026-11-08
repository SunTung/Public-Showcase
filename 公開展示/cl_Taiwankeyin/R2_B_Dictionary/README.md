# cl_Taiwankeyin R2-B｜Terra Pinyin → Bopomofo dictionary importer

This **optional standalone importer** extends the tested R1/R2-A sources rather than changing either baseline. It requires ICU's **Latin-Bopomofo** transliterator and supports source Rime Terra Pinyin dictionary rows in `word<TAB>tone-number-pinyin[<TAB>weight]` format, after the YAML `...` header marker.

## Compile and verify

```sh
cmake -S R2_B_Dictionary -B build-r2b -DCMAKE_BUILD_TYPE=Release
cmake --build build-r2b --parallel
ctest --test-dir build-r2b --output-on-failure
```

## Import a full upstream dictionary

1. Obtain the **upstream** `terra_pinyin.dict.yaml` from https://github.com/rime/rime-terra-pinyin (not included in the repository or ZIP).
2. Run: `./build-r2b/cellkeyin_import_terra terra_pinyin.dict.yaml my_zhuyin_tw.tsv`.
3. Use the output with `./build-r2b/r2a/cellkeyin_r2_cli my_zhuyin_tw.tsv :memory:`.
4. Inspect `accepted`, `skipped`, `duplicate` counts. Validate word counts, pronunciation examples, Taiwan preferred orthography and duplicate/readings before release.

### Engineering properties

- Converts every numeric pinyin syllable using ICU `Latin-Bopomofo`. ICU omits first tone, so the importer explicitly appends `ˉ`; it checks the remaining four tone marks.
- Converts multi-syllable pinyin to space-separated canonical Bopomofo as understood by R2-A.
- Enforces at most ten effective characters; malformed pronunciations, records with syllable/character count mismatch and repeated reading/word pairs are skipped and counted.
- Writes only to a **new output filename**; does not silently overwrite an existing dictionary.
- This smoke test uses **synthetic examples** and does not establish that the full 99k-line upstream corpus has been imported or validated. Upstream download remained unavailable in the execution environment.
- Baseline weights are intentionally uniform (`10`) until a verified language frequency dataset and ranked-candidate benchmark exist; this avoids treating upstream line order as calibrated rank.

### Provenance

Rime's `rime-terra-pinyin` upstream repository is labeled LGPL-3.0. The currently referenced upstream dictionary header also cites CC-CEDICT/CC-BY-SA 3.0 content and other sources. These belong to the **external upstream dataset**, which is not bundled in this distribution. Preserve and evaluate its original provenance and applicable terms before redistributing derived corpora. The CELL importer source code here is independently authored.
