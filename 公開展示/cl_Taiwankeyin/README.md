# cl_Taiwankeyin｜繁體細胞注音輸入法（Windows + Android）

## Android 手機版（2026-11-08）

- [AndroidMobile 原生 Android IME 工程](AndroidMobile/)：Java 版大千注音鍵盤、候選列、十字經驗記憶、SQLite、本機詞庫匯入。
- Android 平台核心 116/116 Java 測試通過；Android Manifest/XML 結構已檢查；公開程式檔案逐檔讀回 19/19 一致。
- [Android Debug APK 已編譯成功](https://github.com/SunTung/Public-Showcase/actions/runs/42475919495)：可從 [Google Drive 下載 APK](https://drive.google.com/file/d/1ScIZjfTvC52iBRveVWTmy9jcmOEIRa_Y/view)，或 [查看 APK 驗收報告](AndroidMobile/docs/APK_CI_ACCEPTANCE_20261108.md)；**手機實機安裝與試打尚未驗收**。
- [手機版工程報告](AndroidMobile/docs/ENGINEERING_REPORT_20261108.md) · [Windows / Android 版本關係](AndroidMobile/docs/SOURCE_LINEAGE.md)。
- 手機版是對既有 R1、R2 的 **Java 功能移植**，沒有修改原有的 Windows C++ 核心，也不把測試用小詞庫稱作完整詞庫。

---

## 最新可驗證進度（2026-11-08）

| 階段 | 實際狀態 | 原始碼／證據 |
| --- | --- | --- |
| R0 規劃 | DONE | [PLAN.md](PLAN.md) |
| R1 C++17 十字細胞記憶 | Linux 37/37 PASS | [R1_CppCore](R1_CppCore/) |
| R2-A 大千注音組字與候選 | Linux 167/167 PASS；ASan/UBSan PASS | [R2_Zhuyin](R2_Zhuyin/) |
| R2-B 可擴展注音詞庫轉換器 | 合成詞庫導入、9項驗證、四組 CTest PASS；ASan/UBSan PASS | [R2_B_Dictionary](R2_B_Dictionary/) |
| R2-B 全量公開詞庫 | 轉換接口就緒；真實完整詞庫尚未在本地環境導入驗證 | [自動化 CI](../../.github/workflows/cl_taiwankeyin_r2b.yml) |
| R3 Windows 測試 EXE | 未編譯／未實機測試 | 待執行 |
| R4 系統 TSF DLL | 未實作／未安裝 | 待執行 |
| R5 發行版 | 未完成 | 待執行 |

目前實作：完整37根大千注音鍵位與五種聲調、逐鍵組字、退格、選字、候選排序、已確認詞彙才學習、10有效字的上下文、括號與冒號跨段關聯、一般標點斷句、SQLite WAL 本機經驗詞庫。

**注意：目前是可在 Linux 執行的 CLI＋C++ 工程，尚未提供 Windows 的 `cl_Taiwankeyin.exe` 或 TSF DLL。** 完整大型繁體詞庫也尚待全量匯入及驗收；附帶的小型測試詞庫不能視為成品。

公開區域僅保存可公開原始碼與合成測試資料；不會公開使用者輸入歷史、個人 SQLite 或未公開的 CELL 核心。Google Drive 專案工作區保存獨立完整來源 ZIP 與驗收報告。
