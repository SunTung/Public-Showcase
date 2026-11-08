# CELL TaiwanKeyin Android｜來源關係與工程邊界

原工程：cl_Taiwankeyin，原始規格 2026-11-08。
- R1 C++17 十字上下文核心：SunTung/Public-Showcase/公開展示/cl_Taiwankeyin/R1_CppCore。
- R2-A C++17 大千注音：SunTung/Public-Showcase/公開展示/cl_Taiwankeyin/R2_Zhuyin。
- R2-B 大型詞庫轉換工具：SunTung/Public-Showcase/公開展示/cl_Taiwankeyin/R2_B_Dictionary。
- Android mobile `app/src/main/java/tw/cell/taiwankeyin/core/KeyinCore.java` 是 **獨立 Java 功能移植**，不是使用 NDK/JNI 編譯上述 C++ 原始檔。
- `app/src/main/assets/seed_zhuyin_tw.tsv` 為原始 R2-A 手工測試詞庫的逐字節原版，不是通用正式詞庫。

## 行為對照

| 項目 | R1 / R2 C++ | Android Java alpha1 |
|---|---|---|
| 大千37注音 + 五聲調 | R2-A | 已實作 |
| 預組字/候選/選字確認 | R2-A | 已實作 |
| 十字滑動窗 | R1 | 已實作 |
| 括號/冒號軟連接、句讀硬斷句 | R1 | 已實作 |
| 跨次選字加權 | R1 | SQLite Java 重寫，非相同分數 |
| 字素切割 | ICU C++ | Java 合併規則近似，未保證完整 UAX #29 |
| 全量詞庫 | 轉換器已驗證；資料待驗證 | 可匯入 TSV，內建僅測試種子 |
| Windows TSF | 後續 R4 | 不適用 |
| Android InputMethodService | 不適用 | 已寫實作，待 Android 編譯及真機驗收 |

## 保護原始碼及私人資料

Android 原型是新子工程，修改不回寫舊 R1/R2 C++ 檔案。公開 GitHub 僅提交原始碼、測試、少量合成詞庫；不提交使用者私有 SQLite、裝置詞庫備份、帳號或輸入紀錄。
