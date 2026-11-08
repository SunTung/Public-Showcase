# CELL 臺灣注音 v1.0.1 — 彈性按鍵＋每鍵重新配色

日期：2026-11-08。正式唯一套件 ID `tw.cell.taiwankeyin`，versionCode 101，versionName `1.0.1-unified`，沿用 v1.0.0 發行簽章憑證。

## 視覺互動

- 膠質彈性按鍵回饋：觸控時約65ms漸變膨脹／圓角，放開約240ms回彈；觸控命中幾何維持不變，相鄰快速輸入時僅視覺表面重疊。
- 六種既有主題深藍、深灰、紫、綠、暖橙、淺色；第七色塊「彩」啟用「每次按下任何鍵，整個鍵盤按鍵重新隨機配置顏色」。
- 僅使用六組既有可辨識 accent，逐鍵抽籤；每個按鍵下一次不能跟自己上次完全同色。新配色更新現存 GradientDrawable，**不重建 View 或觸控幾何**，以免重置彈性動畫。
- 依背景亮度切換深／淺文字；調色框自身色彩固定以便關閉隨機模式；`theme_index=6` 儲存隨機模式，回到固定色可一鍵取消。
- 候選、注音上字、英文/符號、字詞庫、SQLite 十字經驗記憶邏輯與原本完整詞庫保持不變。

## 本輪驗收證據

- Java 17 portable regression **763/763 PASS**，包含150輪隨機色重選、色域及文字對比測試。
- GitHub 改版 commit `aae541f99628ed8eaec219ed053bf6ff98984abe`；模擬器測試腳本修復 commit `e618e5587703268943732b4646045daf9a6361da`。
- [APK CI 編譯 #42496181137](https://github.com/SunTung/Public-Showcase/actions/runs/42496181137)：SUCCESS。公開 runner 只產生 unsigned release。
- Android 35 初次模擬器 #42496181058：失敗原因為測試腳本仍指向已廢止 `alpha3test`，實際訊息「Activity class ... does not exist」。已修正指向 `tw.cell.taiwankeyin` 並啟動 [模擬器重測 #42496460708](https://github.com/SunTung/Public-Showcase/actions/runs/42496460708)。**重測完成狀態以該 run 為準。**
- 私有固定簽章：APK v2/v3 驗證通過，發行憑證 SHA-256 `347b51f0c52352e5b2a0047201c37a8c8e9913c0df805c1ab7a54c08881135b6` 與 v1.0.0 相同。
- 正式 signed APK：7,771,044 bytes，SHA-256 `cf9e84d4b234351f487852bd346ccc2077b0674d7831aabff03a74a2d1cd5aa0`。
- 從 Google Drive 回讀 signed APK 的 SHA-256 完全一致。
- 同一正式套件 ID、相同簽章與遞增 versionCode 讓 v1.0.1 能覆蓋 v1.0.0，而不會新增 Alpha 測試版 App。
- Android 16 真機鍵盤動畫視覺與個人觸控體驗仍待使用者驗收。

## Google Drive 備份

- [已簽 v1.0.1 APK](https://drive.google.com/file/d/1_kPc2hiqrK30WfkDCPBcpncUuB7BAfnK/view)
- [最後修復的原始碼 ZIP](https://drive.google.com/file/d/1ZB5-TlNHjM1LVPgeceH_feJWFkRWKeoJ/view)
- [建置 unsigned bundle](https://drive.google.com/file/d/1lCGXNarfMRJWLPCOGbc_OKJOaEXBtctY/view)
- 官方詞庫經同等固定來源重建的 158,905 條索引仍內建於 APK。
