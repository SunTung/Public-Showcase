# CELL 臺灣注音 Android Alpha5｜第一排鍵位與六色調色工程驗收

版本：0.1.4-alpha5-test（Android Debug APK）
GitHub 實作 commit：dbf66101e4c4d101b5f6ffe9609ef303ad3d7dc6
流程標籤 commit：966d1f4d9aa36015d3cb744a7d48947214516550

## 實際修改
1. 原第四排數字鍵注音根鍵 `125890-`（7個）搬到**第一排**；五個聲調同排，共12鍵，符合使用者熟悉的實體鍵盤上排位置。
2. 其餘三排注音維持 `qwertyuiop`／`asdfghjkl;`／`zxcvbnm,./` 的對應位置，完整37根鍵不變。
3. 主注音排45dp、上方數字/聲調列37dp、下方標點＋色票列29dp、功能鍵46dp、候選列42dp，移除多餘上方padding。
4. 下方標點旁新增6種可直接點選的色塊：深藍、深灰、紫、綠、暖橙、淺色；點後同步更新背景、普通鍵、功能鍵、候選色及文字色，選擇存入 `SharedPreferences.theme_index`。
5. 保留 Alpha4 全部詞庫、可選聲調、英文 Shift/CapsLock、六頁符號表及 CELL 十字記憶，使用新 package ID `tw.cell.taiwankeyin.alpha5test` 與 Alpha4 並存。

## 驗收
- 純 Java 回歸：**293/293 PASS**。
- [APK GitHub Actions #42492382617](https://github.com/SunTung/Public-Showcase/actions/runs/42492382617)：**SUCCESS**，包含完整詞庫產生、APK Gradle 編譯及 Artifact 上傳。
- [Android 35 模擬器 #42492333373](https://github.com/SunTung/Public-Showcase/actions/runs/42492333373)：**SUCCESS**，含實際 Android EditText、SQLite 整合。
- APK 名稱 `cl_Taiwankeyin_Android_Alpha5_20261108.apk`，8,951,211 bytes，SHA-256：`1f9ddcdcc1f451c32553fe15879acc31cc1c5c6e388106d6b7cda0a69894f298`。
- APK 中實際解出 `assets/full_zhuyin_mobile.sqlite3`，27,340,800 bytes，資料筆數 **158,905**；SQL `PRAGMA integrity_check` = `ok`。

## 備份
- [Google Drive Android 專案資料夾](https://drive.google.com/drive/folders/1UOZumYikN0ygC-y9JSt6vGVHWnAf_IsJ)
- [Google Drive 完整 Alpha5 原始碼 ZIP](https://drive.google.com/file/d/1Ybq1o9wbnBL2V-kPcZinnCZqAbbm7Lpp/view)
- [Google Drive Alpha5 APK GitHub CI Artifact ZIP](https://drive.google.com/file/d/1GYYoQbb4kRSHqPOjDpiF43Z2hJ-kLXbu/view)：解壓得 `app-debug.apk`。
- [GitHub AndroidMobile 工程](AndroidMobile/)

## 尚未驗收
用戶 Samsung Android 16 上的按鍵高度、色票觸控反應、色彩對比及長期輸入體驗，需要實機試打。CI Android 35 測試不等於使用者實機 UX 成功。
