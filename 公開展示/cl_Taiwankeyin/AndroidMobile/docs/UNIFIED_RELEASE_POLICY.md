# CELL 臺灣注音｜單一正式版遷移規則 v1.0.0

- 正式 applicationId：`tw.cell.taiwankeyin`；不再對 debug／release 加入 `.alphaNtest` 後綴。
- Alpha 1～5 的不同 ID 已被 Android 當成多個獨立 App，**無法透過同名 APK 自動合併其私人 SQLite 內容**。
- 既有 Alpha 個人詞庫若需保留，請在卸載前先完成可用的資料匯出；當前原型不提供跨版本自動遷移，請勿承諾舊版資料自動合併。
- 統一版的 **release APK 使用同一份長期保留的私有簽章**；GitHub 公開 CI 不儲存金鑰，只編譯未簽署 release，再在私有環境簽章。絕不可把公開 runner 的臨時 debug 簽章作為正式版。
- 使用者首次安裝統一版後，今後只更新相同套件 ID + 相同簽章，versionCode 遞增。
- UI 與功能保留 Alpha5 的 158,905 筆資料、上排大千數字鍵／聲調、QWERTY、Shift/Caps、符號頁、六色調色塊、十字記憶。
- 在發行正式簽署 APK 前，狀態仍是 `BUILD_OPEN`。真機安裝及舊版學習資料未進行自動搬遷驗證。
