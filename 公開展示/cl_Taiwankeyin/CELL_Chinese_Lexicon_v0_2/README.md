# CELL 中英繁簡共用概念字典 v0.2

**獨立 CELL 自編資料工程；不是既有 Chewing 158,905 筆字庫的改名或清洗版。**

- 以 v0.1 自編 90 概念為已存在的起始資料，保留其語意與欄位；另加入新一批 CELL 整理的中英繁簡對照詞條。
- 以 `concept_id` 連接 zh-Hant-TW / zh-Hans-CN / en；`domain` 和 `pos` 用於語境。詞形相同不代表義項相同；例如 computer `function` 與 mathematical `function` 分開。
- `pronunciation` 獨立存注音與漢語拼音。新詞條**尚未審核讀音，因此不偽造音標**；原 90 個種子讀音仍標 `seed_review_pending`。
- `form_ambiguity` 明記「发、后、干、里」一對多；`relation` 和 `review_event` 提供將來人工及多來源驗證的接口，不臆造跨詞關係。
- `expression.review_status` 區分舊種子和新草稿；未來可按審核階段決定能否進入正式輸入法。
- 完整 SQLite 與 UTF-8 JSON export 可供 Android / Windows / Python / CELL 代理人等跨平台重用，*目前尚未整合到 Android APK 正式候選引擎*。

## 建置 / 驗證

```bash
python src/build_dictionary.py
python -m unittest discover -s tests -v
python -c "import sys;sys.path.insert(0,'src');from build_dictionary import export;export('build/cell_concepts.sqlite3','build/cell_concepts.json')"
```

## 已知品質門檻與後續

- 現在是有限概念集，不是完整英漢、繁簡、注音或拼音辭典。字義、地區用語和音節需要更大樣本的獨立查證。
- 新詞 `draft_review` 不直接導入生產輸入法；先進行多義詞拆分、詞性/讀音校正、來源比對和抽樣複核。
- 後續新增繁簡異體字圖譜、詞形互譯規則、語境例句與英文多義標籤，再對 Android/Windows 做可回退雙庫測試。
- 檔案內只保存 CELL 自編字詞和結構，不置入其他產品品牌/內部編碼，亦不把外部資料複製進入自編 seed。此描述不表示通用詞本身來自 CELL 發明。
