# cl_Taiwankeyin Android Alpha 2｜按鍵尺寸與無聲調選字修復

日期：2026-11-08（Asia/Taipei）
版本：0.1.1-alpha2 (versionCode 2)
來源：延續 AndroidMobile alpha1；未修改 Windows R1/R2 C++ 核心與原始 SQLite 架構。

## 問題與修復

1. **鍵盤按鍵過大**：原注音排版每列 7 個按鍵（共 6 排），而選聲調列只有 5 鍵、被拉滿寬度；改用 10 欄等寬、4 排 × 10 槽容納 37 注音，剩餘位置使用不可點擊的 Space，聲調 5 鍵與常用標點 5 鍵共列。注音鍵從 7 槽寬縮至 10 槽寬；鍵盤整體比原先少 2 列。此為 layout 源碼修復；各種手機寬度的觸控驗收仍待實機。
2. **沒有聲調不出字**：既有 Session 只在按下 ˉˊˇˋ˙ 後提供候選。新增依「移除聲調後的注音鍵」建立索引，未標聲調時展開所有符合的讀音，明確標記的聲調仍嚴格篩選。全詞候選優先，詞典未命中時多音節 fallback 仍可合併。
3. **空白鍵不確認**：系統鍵盤內「空白 / 選字」按鍵在有候選時確認候選首字，真正寫入 Android InputConnection 且回報成功後才學習，不再把空白當成 ˉ 聲調。無組字時保持一般空白；無匹配且未完成時不丟失預組字。實體空白鍵事件也走相同流程。
4. **自動音節推進**：若正在輸入的音節已完成，下一個聲母不能接在既有韻母後時，系統將前一音節設為「聲調未指定」，並開始下一音節；例如「ㄋ ㄧ ㄏ ㄠ」可直接匹配「你好」。
5. **退格兼容**：將第二音節退格到空後，候選自動恢復前一音節；退回前一音節仍可查無聲調候選。多音節上限 10 仍維持。

## 已實際執行的測試

- 在本環境執行 `bash tests/run_java_tests.sh`：**197/197 PASS**，保留並通過原 116 項檢查。新增無聲調「ㄏㄠ→好」、無聲調「ㄋㄧㄏㄠ→你好」、候選立即可見、聲調混用、無聲調退格、10 音節上限、明確錯誤聲調不匹配等測試。
- Android SDK 與 Gradle 未安裝於本地容器；**alpha2 尚未在此處建置 APK 或實機測試**。CI 修復後需以新的 GitHub Actions 執行結果確定打包與上傳狀態，不可引用 alpha1 成功結果冒充 alpha2。

## 並存安裝的簽章處理

已比較 GitHub CI Alpha1 APK 與 Alpha2 初版 APK 的 APK Signing Block v2 內憑證指紋，發現不同。Alpha1 cert SHA-256 為 `dfde7e5b1cbd461e00c1f44d540911c529f0248ea3c1904d54f100e6d1b2234e`；Alpha2 初版為 `f902518262bbfbea24a2cedee9ef623b806739ce6a470c801d14e4be1ca439d7`。故 Alpha2 Debug 套件改用 `tw.cell.taiwankeyin.alpha2test`，顯示「CELL 臺灣注音 Alpha2 測試」，使原有 Alpha1 的 SQLite 學習資料不需先卸載即可保留。並存安裝仍待 Android 手機實測。

## 保留及限制

- 仍只在 Android InputConnection 確認成功後記憶選字；不記錄未選注音，維持密碼欄位隱私保護。
- R1 的有效字數最多 10、括號與冒號跨上下文、通常標點斷句規則未改。
- 目前仍內建有限的手工示範詞庫，不是完整繁體注音輸入法；使用者可另匯入 TSV。
- 建議實機驗收：三星 Android 手機、手機直向／橫向、記事本／瀏覽器／聊天程式、標點跨文記憶、密碼欄位不記憶、連續輸入與退格。

## 證據與來源

- alpha1 已成功 Android CI：https://github.com/SunTung/Public-Showcase/actions/runs/42475919495
- 本階段修改檔案：`app/src/main/java/tw/cell/taiwankeyin/core/KeyinCore.java`、`app/src/main/java/tw/cell/taiwankeyin/android/TaiwanKeyinImeService.java`、`tests/KeyinCoreTest.java`、`app/build.gradle`、文件及 HASH 清單。
