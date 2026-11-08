# cl_Taiwankeyin Android Alpha 1｜APK CI 驗收報告

日期：2026-11-08（Asia/Taipei）

## 來源與實際結果

- 初始 GitHub Actions: https://github.com/SunTung/Public-Showcase/actions/runs/42475284999
- 首次 Run #1：FAIL。核心 Java 測試 PASS；Android SDK setup FAILED，因 setup-android@v3 預設要求已不存在的 `tools` 套件。
- 精確錯誤：`Warning: Failed to find package 'tools'` / `sdkmanager failed with exit code 1`。
- 修復 commit: `f5612feebcf9afab385977271761f0b0fd8a374d`。升級 `setup-android@v4`，設定 `packages: ''`，再獨立安裝 `platform-tools`、`platforms;android-35`、`build-tools;35.0.0`。
- 修正後 Run #2：https://github.com/SunTung/Public-Showcase/actions/runs/42475919495
- 新執行結論：**SUCCESS**，包括 Java 核心測試、Android SDK 35 安裝、Gradle `:app:assembleDebug`、檔案存在性驗證、Artifact 上傳五項關卡。
- GitHub Artifact ID：`13615049398`，名稱 `cl-Taiwankeyin-Android-alpha1-debug-apk`，GitHub 保留期 14 天（預期至 2026-11-22）。
- Artifact 解壓得到 `app-debug.apk`，檔案大小 35,809 bytes；已檢查 ZIP 容器包含 `AndroidManifest.xml`、`classes.dex` 及詞庫 `seed_zhuyin_tw.tsv`。
- APK SHA-256：`7683e9b1092235468162a076aa6087703888c3c61f490f71e26b6d0aa4a6e184`。

## 永久備份

- Android 原始碼：https://github.com/SunTung/Public-Showcase/tree/main/%E5%85%AC%E9%96%8B%E5%B1%95%E7%A4%BA/cl_Taiwankeyin/AndroidMobile
- APK Google Drive：https://drive.google.com/file/d/1ScIZjfTvC52iBRveVWTmy9jcmOEIRa_Y/view
- 原始 GitHub Artifact ZIP Google Drive：https://drive.google.com/file/d/1e6XrKCeohfYupRet3CjsOFqVcryTL6RC/view
- Google Drive 上 APK 已重新讀回，比對 35,809 bytes 與 SHA-256，與本地 CI 下載完全一致。

## 尚未驗收

本次是**可下載的 Android Debug APK**，而非正式簽章的發行版。尚未在實體 Android 手機驗證安裝、Android 輸入法啟用、各 App 打字、SQLite 在 Android 真機的操作與效能；種子詞庫仍非完整臺灣繁體詞庫。不能以 CI 編譯成功等同完整產品驗收。
