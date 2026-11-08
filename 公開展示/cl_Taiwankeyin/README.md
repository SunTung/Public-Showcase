# cl_Taiwankeyin｜繁體細胞注音輸入法（Windows）

## 目前進度（2026-11-08）

- **R0 規格基線**：已完成。[PLAN.md](PLAN.md)
- **R1 C++17 核心**：已實際 Linux 編譯；37/37 單元檢查通過，Debug ASan / UBSan 重測通過。[完整原始碼](R1_CppCore/) · [R1 驗收報告](R1_CppCore/docs/R1_REPORT_20261108.md)
- **R2–R5**：大千注音組字、繁體詞庫、Windows GUI/EXE、TSF DLL 與安裝包尚未完成。

## 已實作功能

最多10個 Unicode 有效字的滑動上下文；遇「，。！？、；」或半形對應符號斷句；遇「（）〔〕〈〉｛｝：」保留跨符號上下文；已確認輸入的短句 n-gram 經驗、候選排序、SQLite WAL 本機持久化，以及清除/敏感模式接口。

完整可安裝 Windows 輸入法必須另外實作 **TSF DLL**。R1 提供的 CLI 僅供核心回歸測試，不是全系統輸入法，也沒有提供 Windows EXE。

## 資料與備份

本公開倉庫只保存可公開的工程原始碼、測試用例、規劃、測試報告與 SHA-256；私人 CELL 原始碼、個人打字歷史、詞庫與帳號憑證不得進入公開目錄。

- Google Drive 主工作區保存 R0 規格與 R1 原始碼 ZIP；公開 GitHub 主體使用 R1_CppCore/。
- 原始碼可依 [R1 README](R1_CppCore/README.md) 建置；未經 Windows TSF 驗收不得宣稱已提供可安裝注音輸入法。
