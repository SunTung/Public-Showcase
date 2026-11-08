# v1.0.1 Elastic + 隨機配色（增量）

保留唯一正式套件 `tw.cell.taiwankeyin`、versionCode 101 與長期簽章。第七種下方色塊「彩」可開啟隨機模式；每次點按注音、英語、符號、功能鍵或候選時，將畫面上所有主鍵逐一重新配置為既有六種配色中的一種。顏色即時改變但鍵位、觸控區與彈性形變動畫保持獨立。設定記入 `keyboard_settings/theme_index=6`；點選任一固定色塊即可取消。

# v1.0.1 統一正式版｜Elastic Key 動態回饋

本次沿用 **tw.cell.taiwankeyin** 唯一正式套件 ID，versionCode 101。保留 158,905 筆完整離線詞庫、十字記憶、六色調色框、第一排數字列注音＋聲調、QWERTY/英文大小寫與符號頁。

按下時每鍵 65ms 內放大到 112.5%、圓角 7dp→23dp；放開後 240ms 恢復。相鄰鍵快速連續觸發時，兩個動畫同時存在、視覺邊緣短暫擠壓，隨後恢復縫隙。實際點擊判定範圍、位置、鍵距、鍵盤外框完全不改。使用者可在設定頁關閉動畫。

更新必須使用 v1.0.0 統一版的同一張簽章憑證；GitHub Actions 僅編譯 unsigned Release，不在公開 CI 保存正式簽章或密碼。

# Android Alpha 5 — 實體數字列優先＋快速調色（2026-11-08）

- 最上排：大千實體數字列 125890- 的七個注音根鍵，緊接五個可選聲調鍵；下方保留 QWERTY、ASDF、ZXCV 三排注音。
- 下方常用標點四鍵旁放置六個色塊：深藍、深灰、紫色、綠色、暖橙、淺色。直接點選立即套用，並以 SharedPreferences `theme_index` 記住。
- 注音主鍵改為 45dp 高，數字/聲調排 37dp，底下標點/調色排29dp；候選條42dp。相較 Alpha4 精簡高度而不縮小主要注音字型。
- 按鍵函數、單音及完整詞庫、可選聲調、英文 Shift/CapsLock、六頁符號表維持原本行為。Alpha5 Debug 使用獨立套件 ID `tw.cell.taiwankeyin.alpha5test`。
- 本輪需以 GitHub Actions Android APK 編譯與模擬器測試結果驗收，不以 JVM 單元測試替代實機 UX。

# cl_Taiwankeyin Android｜CELL 繁體細胞注音輸入法

## Alpha 4：完整字詞庫與日常鍵盤（2026-11-08）

- **手機版改用 Google Drive 已有 RGOS/CELL 詞庫工作的來源及驗收基線**：釘選 Chewing 官方 CSV 上游 commit `c44e81aef24b06f1509f19e1be54c99812d0c43f`、兩個 Git Blob SHA、OpenCC 1.4.2 `s2twp`，重新產生可離線查詢的 SQLite 索引。CI 要求 158,905 條字詞對、133,505 條多音節詞、121,377 個讀音，不接受小詞庫冒充完整詞庫。
- 原始 RGOS 私人倉庫 SQLite 不複製到公開 GitHub，CI 使用等價、已核對的**公開字詞來源**重建 Android 索引；經 CI 實測前，以上數量是來自既有 RGOS 驗收基線而非本次 Android 新版的完成聲明。
- 注音鍵採熟悉的 **QWERTY 位置對照大千鍵位**，37 根鍵全部保留；不再僅依 ㄅㄆㄇ 的字典順序擺放。
- 英文鍵盤提供 Shift 一次大寫、Caps Lock 連續大寫及小寫；符號鍵盤設 **常用／數字／括號／數學／貨幣／特殊** 六頁。
- 只有鍵盤主輸入區，沒有多餘說明標題；聲調區保持精簡。
- 直接用系統 SQLite 查候選，不把 15.9 萬條字詞全載入 Java Heap。保留 Alpha3 已修復的 `commitText`/SQLite 崩潰防護與十字經驗記憶。
- Android Debug 使用獨立套件 ID `tw.cell.taiwankeyin.alpha4test`，以便與 Alpha1/2/3 並存，避免 debug 簽名差異導致覆蓋升級失敗；每版使用各自資料庫。

**建置說明：** APK CI 必須先執行 `tools/stage_verified_full_lexicon.py --download` 將已驗證詞庫放入 `app/src/main/assets/full_zhuyin_mobile.sqlite3`；GitHub 公開原始碼只保存生成器與資料來源記錄，不將 RGOS 私人資料庫直接公開。Android Studio 離線建置前亦需先準備該 asset。


**Android 輸入法工程 alpha3（0.1.2-alpha3-test）**；承襲已通過 GitHub Actions 編譯的 alpha1，新增無聲調自動選字與觸控鍵盤縮放修復。alpha2 APK 的建置結果應以新的 GitHub Actions 執行為準。

平台：Android 8.0+（API 26），系統 IME 使用官方 `InputMethodService` / `InputConnection`。

## Alpha 3｜真實手機故障修復（2026-11-08）

- **Android 35 模擬器已重現確切 SQLite 崩潰：** `ExperienceDatabase.onConfigure` 將會回傳結果的 `PRAGMA secure_delete=ON` 傳給 `execSQL`，Android 拋 `SQLiteException`；已更換為 `rawQuery` 並驗證游標結果。同時修復 `wal_checkpoint(TRUNCATE)` 的同類錯誤。
- [實際程式碼缺陷分析](docs/ALPHA3_ROOT_CAUSE_20261108.md)：先清除組字、後向 Android 提交文字；若目標編輯框拒絕，候選就遺失。已修正為提交成功才清空，並加入 SQLite 錯誤保護。
- 取消鍵盤上方 37dp 永久標題和教學字樣，僅保留動態候選列。
- 聲調/標點排高度由 49dp → 36dp；保留每排10個等寬主注音鍵。
- 本機 JVM 回歸 **215/215 PASS**；另新增 Android Emulator 中實際 EditText/SQLite 的 Debug 整合測試。
- Alpha3 Debug 套件 `tw.cell.taiwankeyin.alpha3test` 可與 Alpha1、Alpha2 並存，不覆蓋兩版學習資料。Android APK/模擬器與真機狀態請以該版 CI 和驗收報告為準。

## 功能（目前實作）

- 37 個大千注音根鍵、五聲調（可選）、候選列、單字與多音節組詞、退格、英文字母切換、常用繁體標點。
- 不用按聲調即可顯示候選，按「空白 / 選字」確認第一候選；連續輸入下一個聲母時會自動推進音節。
- 手機注音按鍵改為四排，每排 10 個等寬格；第五排混合可選聲調與常用標點，減少過大的第一排按鍵。
- 最後 **10 個有效字元** 的 CELL 經驗窗；遇 `，。！？、；` 與半形對應標點斷句；`（）〔〕〈〉｛｝：` 保留連接。
- 只在 Android 編輯框確認接收文字後記入本機 SQLite；未選字時不學習。
- 個人選字、上下文關聯與最多 10 字短句經驗；支援學習開關、清除資料、密碼欄位不學習。
- 匯入由 R2-B 產生的 UTF-8 TSV 詞庫（reading<TAB>word<TAB>baseline）。內建示範詞庫來自 R2-A，**不是完整量產詞庫**。
- 禁止系統自動備份使用者學習資料。未使用網路權限，輸入資料僅儲存於裝置內。

## 安裝與開啟

1. 使用 Android Studio 開啟本資料夾，採 JDK 17 / Android SDK 35 / AGP 8.9.2。
2. 執行 Gradle `:app:assembleDebug`；APK 位於 `app/build/outputs/apk/debug/app-debug.apk`。
3. 在 Android 上安裝 APK，開啟 **CELL 臺灣注音** App。
4. 按「開啟 Android 輸入法設定」啟用；再按「選擇 CELL 臺灣注音鍵盤」。
5. 點「試打區」或在其他 App 的文字欄位開始使用。

> GitHub Actions workflow: `.github/workflows/cell-taiwankeyin-android.yml` under the public repository root. On every AndroidMobile folder update it runs headless tests and builds a debug APK artifact.

## 結構與版本關係

- `core/KeyinCore.java`：R1 Context10 + R2-A phonetic/selection contract 的 **Java 行為移植**；不是 C++ JNI 直接連結。R1/R2-A C++ 基線保留不變。
- `android/TaiwanKeyinImeService.java`：Android InputMethodService，真正把字寫入當前編輯框。
- `android/ExperienceDatabase.java`：SQLite 持久化（裝置私有），不與 Windows 資料共用路徑。
- `android/SettingsActivity.java`：開啟設定、選擇 IME、詞庫匯入、清除學習、試打。
- `tests/run_java_tests.sh`：Android SDK 之外獨立執行的純 Java 測試。

## 當前限制與下一關

- alpha1 已在 GitHub Actions [#42475919495](https://github.com/SunTung/Public-Showcase/actions/runs/42475919495) 成功建置 APK。**alpha2 還需要自己的 CI 編譯結果與手機實機驗收**。
- 臺灣全量繁體詞庫仍待匯入、異音字校對與詞頻驗收；不宣稱已完整可用。
- Android Core Java 版為原生平台行為移植，尚未做與 Windows C++ 的逐案例跨語言一致性全面比對。
- 後續追加完整候選分頁、全符號/英數鍵盤、語音、手勢、emoji、Android 真機性能與防撞誤觸設計。

## 隱私

輸入法在作業系統內具有接觸當前輸入欄位的能力。此原型 **不要求網路權限**、**不記錄敏感欄位文字**，且不使用遠端服務。SQLite 儲存可識別的短語，資料不等於匿名；手機遺失時仍應依賴 Android 裝置加密與螢幕鎖。

## 編譯驗收來源

- [工程紀錄](docs/ENGINEERING_REPORT_20261108.md)
- [R1/R2 與 Android Java 的版本關係](docs/SOURCE_LINEAGE.md)
- alpha2 核心已在 Linux Java 17 通過 **197** 項檢查（alpha1 為 116）。
- [alpha2 修復驗收報告](docs/ALPHA2_FIX_REPORT_20261108.md)；APK 的編譯與真機通過狀態需另查 GitHub Actions。

## Alpha 2 Debug 並存安裝（避免覆蓋 Alpha 1）

因為 GitHub Actions 每次產生的 Debug 簽章憑證可能不同，已安裝的 Alpha 1 不能保證被 Alpha 2 直接覆蓋升級。**本版 Debug APK 採用獨立套件 ID `tw.cell.taiwankeyin.alpha2test`，顯示為「CELL 臺灣注音 Alpha2 測試」，可與 Alpha1 並存，避免要求使用者先清除舊版及其經驗資料。** Alpha2 測試版擁有自己的 SQLite 私有資料庫，不會直接共用 Alpha1 已學資料。正式更新版日後需使用持續穩定的簽章。

## alpha2 的手機試打案例

- **無聲調**：輸入「ㄏ、ㄠ」，候選列即出現「好」，按「空白 / 選字」輸入「好」，**不會額外插入空格**。
- **音節自動推進**：依序點「ㄋ、ㄧ、ㄏ、ㄠ」，候選列出現「你好」，按空白確認。
- **有聲調**：也可先按「ㄏ、ㄠ、ˇ」，再選「好」；指定聲調只篩對應讀音。
- 未組字時空白鍵才會插入一般空白；只輸入了不完整聲母時，按空白保留原始注音以供補全。

目前仍屬小型示範詞庫，無法保證所有中文字都有候選。
