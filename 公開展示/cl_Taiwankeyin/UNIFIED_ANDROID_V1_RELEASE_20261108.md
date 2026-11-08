# CELL 臺灣注音｜單一正式版 v1.0.0（2026-11-08）

## 版本收斂

既有 Alpha 1～5 使用不同 `applicationId`，造成多個並存 Android 輸入法；現將所有已驗證功能整合為唯一正式 ID **`tw.cell.taiwankeyin`**，顯示名稱 **CELL 臺灣注音**，版本 **1.0.0-unified** / versionCode **100**。不再對新版追加 `.alphaNtest`。

## 已完成的交付

- Android 核心保留完整 Chewing 15.9萬筆詞庫、十字記憶、無聲調候選、QWERTY/數字列大千鍵位、英文字母 Shift/Caps、六頁符號與六色主題。
- GitHub 公開 CI： [統一版 Release 編譯 Run #42493942210](https://github.com/SunTung/Public-Showcase/actions/runs/42493942210) SUCCESS；產生未簽署 `app-release-unsigned.apk`。
- 真正 Android 35 EditText/SQLite 模擬器：[Run #42493942177](https://github.com/SunTung/Public-Showcase/actions/runs/42493942177) SUCCESS（測試用 debug 同一 canonical ID）。
- **簽章階段在私有本地完成**，公開 GitHub 不含簽章金鑰及密碼。
- Signed APK 7,771,044 bytes, SHA-256 `8bd2fad915607902457c5dc79448fc80985ca33c9894bfbe5b8eb5820a31507d`。
- APK Signature Scheme v2 PASS、v3 PASS；簽名者 RSA 3072，憑證 SHA-256 `347b51f0c52352e5b2a0047201c37a8c8e9913c0df805c1ab7a54c08881135b6`。
- APK 內包含 `AndroidManifest.xml`、`classes.dex` 與 27,340,800 bytes 的 `assets/full_zhuyin_mobile.sqlite3`。
- Google Drive APK 備份：https://drive.google.com/file/d/1X7jzBCAQ-ogJEKY1Zxrg3eD25TT_XyKu/view
- Google Drive 完成後回讀 signed APK，SHA-256 與本地**完全一致**。

## 長期升級要求

後續發行版必須同時符合：
1. `applicationId` 永久保持 `tw.cell.taiwankeyin`。
2. 使用同一份**私有 release PKCS12 keystore** 與對應密碼簽署；公開 CI 僅提供 unsigned release。
3. `versionCode` 每一版遞增，絕不能低於已安裝版本。
4. 給使用者的 APK 必須驗證簽名憑證 SHA-256 與本基線相同，並再次檢查功能與詞庫。
5. 私有簽章保存在 Google Drive 手機版專案的 `PRIVATE_SIGNING_KEY_DO_NOT_SHARE`，**絕不可公開分享此資料夾或其檔案**；正式 APK 可以公開分享。

## 安裝與資料安全邊界

- 原本 Alpha1～Alpha5 的 Android package ID 不同；**新的統一版是一次性獨立安裝，無法憑改名直接取得舊版 app-private SQLite 學習資料**。
- 未確認已備份的舊版使用者學習資料前，請不要為了清理而立即卸載仍需保留資料的舊版。刪除舊版 App 一般會刪除其私人資料；完整系統詞庫已另備份，不受影響。
- 以後 v1.0.1、v1.0.2 等才可按同 ID／同簽章／更高 versionCode 正常覆蓋更新。
- **尚未進行使用者 Samsung Android 16 實體裝置安裝及日常長時間輸入驗收**；CI/模擬器的 PASS 不等於真機完工。
