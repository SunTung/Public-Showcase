> **Play 上架準備版 v1.2（2026-11-11）**：專案現已加入公開開發者資訊入口、AdMob 測試 Banner、Google UMP 同意流程、target API 36，以及 AAB 建置步驟。客服聯絡資料、商店正式簽章與實際上架尚未完成。

# 手機錄音器 PocketRecorder（Android）

**狀態：公開原始碼、可由 GitHub Actions 建置的測試版。**  
版本：v1.1 UI 修正版（2026-10-26）。此版本非 Google Play 正式發行版，手機實機相容性仍須測試。

## 功能
- **錄音**：按「錄音」開始錄製，按「停止」結束並儲存。
- **播放**：播放最新錄音，或從下方清單指定播放。
- **停止**：停止錄音或中止目前音訊播放。
- **新工作**：重置操作狀態，準備下一筆錄音。
- **狀態及計時**：待機中、錄音中、儲存中、播放中、計時器。
- **檔案列表**：名稱、長度、格式、紀錄時間、備註；可播放、改名、修改備註、刪除。
- **麥克風測試**：5 秒音量偵測，不保留測試檔。
- **介面與圖標**：大字、手機直式操作、圓角彩色按鈕、麥克風圖標。

## 安裝
1. 打開本倉庫的 [GitHub Actions](../../actions/workflows/pocket-recorder-public.yml)。
2. 開啟綠色勾號的最新 **Build Public PocketRecorder APK**。
3. 在 **Artifacts** 下載 `PocketRecorder-debug-APK`，解壓縮得到 `app-debug.apk`。
4. 在 Android 手機開啟 APK 安裝，首次使用時允許麥克風權限。

注意：**GitHub Actions 的 Artifacts 在某些手機瀏覽器或未登入狀態可能無法直接下載**。公開原始碼不等於 APK 已發佈至 Releases。本專案目前未設置正式 Release 下載頁。

## 技術規格
| 項目 | 說明 |
|---|---|
| 語言 | Kotlin |
| UI | Android 原生 View |
| 最低系統 | Android 8.0（API 26） |
| 編譯 | Android SDK 35、Gradle 8.9、JDK 17 |
| 音訊 | MPEG-4 AAC（.m4a）|
| 音訊存放 | App 私有資料夾 |
| 網路權限 | 不要求 |
| 麥克風權限 | RECORD_AUDIO |

## 已知限制與提醒
- 目前是**前景錄音**：切到其他 App 或背景可能停止錄音，不適合作為長時間背景錄音工具。
- 錄音檔保存在 App 私有目錄；**解除安裝會使錄音資料可能遺失**。請勿先解除安裝舊版。
- 測試 APK 為 GitHub Actions 產生的 debug 簽名，**與不同電腦或不同 Actions 執行批次產生的 APK 可能無法直接覆蓋安裝**。遇到簽章不一致時，不應直接卸載含有重要錄音的舊版。
- 尚未實作直接匯出／分享錄音、背景持續錄音、定期備份。
- 「變更名稱」更改清單顯示名稱，不改動實體錄音檔案名稱。
- 編譯成功只證明 APK 可產生，**不代表已通過各種手機的錄音和 UI 實機測試**。

## 原始碼
- [MainActivity.kt](app/src/main/java/tw/suntung/pocketrecorder/MainActivity.kt)
- [AndroidManifest.xml](app/src/main/AndroidManifest.xml)
- [圖標設計](app/src/main/res/drawable/ic_recorder_foreground.xml)
- [Gradle 設定](app/build.gradle.kts)

## 授權
目前尚未附上開源授權條款；程式碼可公開閱讀，但不要自行假設已獲授權進行再發佈或商業使用。

## Google Play 上架準備 v1.2

- 應用程式內「開發者資訊 · 隱私權」顯示公開開發者名稱 **SunTung**、GitHub 專案入口與測試版隱私說明。**不包含私人地址、私人電話或未確認的電子郵件**。
- 底部固定廣告容器採 Google AdMob 官方測試 ID；**沒有接入任何實際廣告收益帳號**。
- 在廣告請求前執行 UMP 同意更新，僅在可請求廣告時載入 Banner。
- Android 16 / API 36、建立 Debug APK 與 **unsigned release AAB**；正式上傳 Play 必須使用自己的發布簽章或由 Play App Signing 流程完成上傳金鑰設定。
- 真正上架前須填妥開發者聯絡信箱、AdMob App ID / Banner Unit ID、隱私權政策網址、Play Console Data safety / Contains ads 聲明、商店圖片、正式簽署 AAB，並執行實機與封閉測試。
- **注意：廣告 SDK 可能蒐集／分享裝置識別碼、互動資訊及診斷資訊**，不可再以無網路權限或完全離線蒐集零資料描述本版本。錄音內容本身仍設計為 App 私有本機保存，未主動上傳。

開發者的公開個人資訊與真實廣告 ID 應由本人審核後填入，避免將私人聯絡資料直接暴露在公開 GitHub。

## AdMob 廣告單元設定（2026-11-11）

| 欄位 | 值 |
|---|---|
| 廣告單元名稱 | 橫向banner_細胞麥克風_1_2026_1111A0001 |
| 正式 Banner Ad Unit ID | `ca-app-pub-1343937669240075/3821085574` |
| 正式 AdMob App ID | `ca-app-pub-1343937669240075~7835518057` |
| 目前預設編譯模式 | **Debug：測試廣告；Release：正式廣告** |

- 本專案的 Activity 使用 Kotlin **原生動態 UI**，不使用 `activity_main.xml`；廣告位於主畫面底部的固定容器。
- `app/build.gradle.kts` 已註冊正式 App ID 與 Banner ID。Debug 使用 Google 測試 ID；Release 使用正式 ID，避免混用。
- 正式發布建置：`gradle :app:bundleRelease`，但需配置發布簽章才能交付 Google Play。
- **不要直接複製字串中的 `XXXXXXXXXX` 作為 App ID**，它是待填佔位符。
- 仍須確認 AdMob 後台「應用程式設定」→ **應用程式 ID**；若要測試自己的正式廣告單元，先在 AdMob 設定測試裝置。正式 AdMob Banner 應在正式上架配置與必要同意測試後啟用。
- 所有實際收益由你自己的 AdMob 帳號處理；GitHub 只提供編譯程式，不會接收廣告收益。
