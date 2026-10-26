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
