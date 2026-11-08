# CL TaiwanKeyin｜Windows 繁體細胞注音輸入法
工程規格與實施計畫 v0.1｜2026-11-08
狀態：PLAN APPROVED FOR IMPLEMENTATION（規格基線；不代表 Windows EXE 或 TSF 已驗證）

## 0. 專案定位與最終產物
- 專案名稱：cl_Taiwankeyin（對外中文名：繁體細胞注音輸入法）
- 執行平台：Windows 10/11 x64，繁體中文 zh-TW，預設大千注音鍵盤。
- 使用者要求：以對比經驗記憶「上次輸入內容中十字以內的短句」，以標點符號斷句；但 （）〔〕〈〉｛｝： 不截斷前後文記憶。
- 正式交付：cl_Taiwankeyin.exe（設定/狀態/維護介面）＋ cl_Taiwankeyin.dll（TSF Text Input Processor）＋ cell_keyin_core（C++ 原生核心）＋本機詞庫/使用者資料庫＋安裝與解除安裝工具。
- 注意：EXE 並不等於全系統輸入法；必須有 TSF DLL、COM/TSF 註冊、語言 Profile、候選窗及安裝驗證。無法僅靠一般鍵盤攔截程式冒充 TSF 輸入法。
- 開發原則：不改動既有 CELL 主體；以可替換的 Adapter 介面選擇性接入 CELL 片語/關係引擎；任何既有 CELL 資料需先按已驗證版本與授權範圍檢視，無須無故重測原有基線。

## 1. 實際操作流程
按鍵 → 注音組字 → 查詢繁體字詞候選 → 用戶選定/上屏 → 擷取當前句內最近最多10個有效文字 → 查詢細胞經驗關係 → 候選重新排序 → 累加學習資料 → 安全持久化。
按鍵/預組字不直接寫入學習庫；只針對已確認上屏的文字學習。
標準鍵位：大千鍵盤；一聲空白、二聲6、三聲3、四聲4、輕聲7，聲韻部件按鍵位表完整維護。

## 2. 10字記憶的精確定義
A. 即時上下文窗口（Context10）：目前句段最後最多10個「有效字元」。有效字元採 Unicode 字素簇（grapheme cluster）計數，而非 UTF-8 byte、UTF-16 code unit；漢字、英數字可計入。相容標點為結構資訊，不佔10字名額。
B. 短句經驗庫（Experience10）：從使用者已確認上屏的連續句段，擷取長度1～10有效字的詞組/短句及其相鄰延伸；記錄選詞次數、上一上下文、最近選定時間及糾錯情況。禁止無限制保存整篇原文。
C. 前後文對比：以「注音鍵序、字詞、前綴上下文、上次候選選擇」建立稀疏關聯，對比多個候選；使用者選擇是更新信號，不聲稱具有未驗證的語義理解能力。
D. 單句超過10字：僅保留最近10有效字的滑動窗；學習最多10字片段，不以整篇取代短句限制。
E. 上次輸入：下一次輸入前可從 Experience10 比對上次成功上屏的片段，系統重啟後只保留允許持久化的學習統計，不自動展示原文歷史。
F. 關閉學習或隱私模式：停止保存並允許清除學習記錄。

## 3. 斷句與結構符號規則
- 硬斷句：，。！？、；及其半形對應 , . ! ? ;，另以換行/段落結尾作硬斷句；遇到硬斷句清空即時句段 Context10，將前一段完成經驗結算。
- 軟連接（不斷句）：（ ） 〔 〕 〈 〉 ｛ ｝ ：。連接符保留 token/位置/括號深度；前後文均可用來學習，即使輸入跨越括號/冒號。
- 例如「今天（台南）天氣很好：適合出門。」：括號及冒號兩側可形成關聯，句號結算並重置。
- 例如「台南，安平」：逗號前後不得自動組成同一句的十字關聯。
- 例如「第一章：起點」：「章」與「起點」可關聯。
- 括號內若出現硬斷句符號，仍照硬斷句處理；後續是否支援引號/小數/網址例外，需單獨訂規則與測試，不能私自擴充。
- Unicode 正規化 NFKC 只能用於索引匹配層；輸出不得默默把臺灣正體字/全半形變掉。繁簡字形以繁體 zh-TW 詞庫為準。
- 游標跳轉/反白取代、跨應用焦點切換不得無證據地銜接未知前文；只在可取得且合法的目前輸入上下文中連接。

## 4. 經驗排序與保護基線
候選原始詞典分數 Base + 使用頻次 + 上下文條件次數 + 有衰減的最近使用權重 + 用戶明確糾正（降權）。權重集中在可設定的獨立 Ranker；離線可重播相同輸入/輸出測試。
初始建議 Score(c|z,x) = 1.0*Base(c|z) + 0.8*ln(1+Freq(c)) + 1.2*ln(1+ContextCount(x,c)) + 0.3*Recency(c) - 1.0*RejectCount(x,c)；僅作待實驗起點，不是已證實最佳權重。
首次使用不依賴經驗庫；仍能依繁體字典輸入。自動學習不得將錯誤選字永久鎖定第一候選；支援重設個人權重、匯出匿名統計，保護既有詞典不被修改。
優先支援同音異字：「在／再」、「的／得」、「台／臺」等依語境排序。繁體字形遵照使用者選擇與臺灣詞庫，不強行統一。

## 5. 核心元件與檔案
- core/zhuyin_keymap.*：完整大千鍵位、聲調與候選查詢 API。
- core/segmenter.*：Unicode 字素計數、軟連接、硬斷句及括號配對狀態。
- core/context10.*：即時十字環形窗口。
- core/experience_store.*：SQLite 使用紀錄、資料表版本、交易與清除。
- core/ranker.*：可重播排序（baseline/adaptive）。
- core/cell_adapter.*：CELL 已驗證外部關係模型選配接口；不直接嵌入未核實之既有模型。
- windows/tsf/：TSF COM DLL，ITfTextInputProcessorEx、ITfKeyEventSink、候選 UI/Composition、語言 Profile 註冊/解除註冊。
- windows/app/：設定 EXE、候選模式/學習切換、匿名統計/匯出/資料清除。
- tests/：單元、整合、Windows TSF 人工與自動化驗收。
- packaging/：CMake、Windows CI、ZIP 安裝包與 SHA-256 清單。

## 6. 本機學習資料庫規劃
LocalAppData/cl_Taiwankeyin/user_lexicon.sqlite3，不存至公開 GitHub。
建議表：phrase_stats(phrase_id,normalized_text,grapheme_len,selected_count,last_selected_at)、context_edges(context_hash,phrase_id,count,last_seen_at)、zhuyin_choices(zhuyin_key,phrase_id,count)、settings(schema_version,private_mode)。
跨進程採 SQLite WAL 與單一寫入者或安全序列化；異常終止不得毀損詞庫。
對需要復原的個人輸入，可在設定中明確啟用局部原文儲存；預設僅保留短句學習必要資訊。密碼/金融敏感欄位依 TSF InputScope 及使用者隱私模式停用學習，並防止候選殘留。

## 7. 開發批次與通過門檻
R0（本輪）｜核對 Microsoft TSF 官方資料、固定需求、建立 Drive 專案資料夾與公開 GitHub 規格副本；不宣稱 EXE 已完成。
R1｜C++17 純核心：Segmenter + Context10 + Experience10 + Ranker + SQLite；Linux/Windows 單元測試，輸入輸出可重播，無 Windows 依賴。
R2｜大千注音鍵盤與繁體基礎詞典：組字、聲調、選字、候選視窗模型；人工詞例和客觀測試集。
R3｜Windows 測試 EXE：文字輸入沙盒 + 設定視窗 + 啟閉學習、刪除記憶、選字紀錄；可執行不等於 TSF。
R4｜TSF DLL：COM、語言 Profile、按鍵事件、Composition、候選視窗、x64安裝、解除安裝；記事本、瀏覽器、Word、UWP 典型輸入框實機測。
R5｜安裝打包、Windows 10/11 雙機測試、冷啟動/跨應用/重啟恢復、回歸與可復現成品標籤。
驗收條件：斷句、括號/冒號關聯、十字上限、Unicode、詞序學習、反悔糾錯、重啟持久化、隱私模式、TSF 可安裝/可切換/可輸入/可解除，各項有測試證據；候選準確度則記錄對照實驗，不提前宣稱提升比例。

## 8. 優先測試向量
T01「今天（台南）天氣」：括號不斷，前後候選可連。
T02「第一章：起點」：冒號可連。
T03「今天，明天」：前後句分隔。
T04「abcdefghi中文」：上下文有效字固定最近10字。
T05「你好。世界」：句號切斷。
T06「注音（專業〔詞彙〕）練習」：巢狀括號不斷。
T07「測試｛設定｝通過」：全形大括號不斷。
T08「候選甲→選甲→再輸入同音詞」：個人排序可提升，無練習資料不假定結果。
T09「清除學習庫」：候選恢復原始排序。
T10「密碼欄位」：未落庫；不將相鄰應用文字拼接。
T11「關閉重啟」：受允許的統計恢復。
T12「半形/全形混排」：顯示原文不被索引正規化破壞。
T13「括號內含逗號」：依明定硬斷句，不假裝括號豁免內部逗號。
T14「輸入法註冊→輸入→停用→解除」：Windows R4 必做實機測試。

## 9. 工程資料與公開備份原則
Google Drive（正式工作區）：CELL/cl_Taiwankeyin_WIN_繁體細胞注音輸入法_20261108/。
GitHub（公開副本）：SunTung/Public-Showcase/公開展示/cl_Taiwankeyin/。
公開只包含規格、可公開的原始碼、空白測試詞例、建置方式、測試/雜湊摘要；不公開個人已輸入短句、個人詞庫、私人 CELL 核心/資料、密鑰、私有資料集、執行時資料庫、可能敏感的測試日誌。
Drive 為工作文件；GitHub 為公開唯讀副本/版本紀錄；以版本號+原文內容 SHA-256 比對一致。
所有狀態以「已建立／已編譯／已測試／已安裝」分欄，未完成不得寫 PASS。

## 10. 技術參考
Microsoft Text Services Framework：https://learn.microsoft.com/en-us/windows/win32/tsf/text-services-framework
Microsoft Text Service Registration：https://learn.microsoft.com/en-us/windows/win32/tsf/text-service-registration
Microsoft 官方 IME 範例：https://github.com/microsoft/Windows-classic-samples/tree/main/Samples/IME
大千注音排列參考：https://vchewing.github.io/manual/arranges.html
註音臺灣正體開源方案參考：https://github.com/rime/rime-bopomofo
