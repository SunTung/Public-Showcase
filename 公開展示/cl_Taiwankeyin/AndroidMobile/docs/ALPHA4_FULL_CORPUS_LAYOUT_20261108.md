# CELL 臺灣注音 Alpha4｜完整詞庫及日常鍵盤工程

## 已有權威來源

Google Drive `CELL_RGOS_Zhuyin_IME_ENGINEERING_STATUS_20261108.md` 指向 RGOS 私人倉庫內已測試的完整詞庫：**158,905 筆字詞對／133,505 筆多音節／121,377 讀音**，SQLite SHA-256 `57d3d3f332710d6dcab0bbef997407edeb56ca5e9483652fd42fb7404cc01586`。

本公開 Android 專案沒有私有 RGOS GitHub Actions 存取權限，因此改成在本公開 CI 使用**同一版 Chewing 公開原始 CSV、相同 Git Blob SHA、新酷音資料 LGPL metadata、OpenCC 1.4.2 s2twp**，生成完全獨立的 Android 版唯讀 SQLite 索引。確認條目與候選案例必須通過才能產生 APK；這不代表產出的 Android SQLite 位元組必定等於 RGOS 私人 SQLite，兩者不同 schema。

## 測試關卡

1. 釘選上游 `chewing/libchewing-data` commit `c44e81aef24b06f1509f19e1be54c99812d0c43f`，分別核對 `word.csv`、`tsi.csv` 的 Git blob SHA。
2. 使用 OpenCC 1.4.2 `s2twp` 標準化臺灣詞彙，產生 `lexicon_mobile(bare,reading,word,frequency)`。
3. 核對 rows/multi/readings 三項總數，執行 `PRAGMA integrity_check`，核對常用字詞。未達標即 CI FAIL。
4. Android APK 內必須有 `full_zhuyin_mobile.sqlite3` 與 `full_lexicon_manifest.json`；Android 啟動時將資產複製到 app 私有、無備份目錄，SQLite 唯讀，個人經驗另用原本 WAL DB。
5. Android 模擬器 Debug Probe 驗證 158,905 rows、中文字候選、`InputConnection.commitText`、已驗證的 SQLite 經驗提交流程。

## 注音鍵盤

採用大千與 QWERTY 物理位置對照，不以 ㄅㄆㄇ 自然順序依次排列：

```
q w e r t y u i o p   (對應十個大千注音符號)
a s d f g h j k l ;
z x c v b n m , . /
1 2 5 8 9 0 -       (剩餘七根鍵，補空槽保持等寬)
ˉ ˊ ˇ ˋ ˙ ， 。 、 ？ ！ (薄聲調與標點列)
[ABC] [符號] [空白／選字] [⌫] [↵]
```

英文按 ABC 進入三排 QWERTY，Shift 單次大寫、再按切入 Caps Lock，第三次回到小寫。符號鍵按頁切換，共六頁至少 100 個符號，不再只依賴主注音頁的五個符號。

## 版本安全與驗收界線

Alpha4 Debug 獨立 package `tw.cell.taiwankeyin.alpha4test`；不修改 Alpha1/2/3 私人學習記憶。既有完整字詞的二次整理屬可重現的公有源衍生建置，不自行宣稱對原公開字詞有專屬版權。`GitHub CI PASS` 只代表編譯與模擬器驗收，不代表 Android 16 Samsung 手機的人機工學驗收。
