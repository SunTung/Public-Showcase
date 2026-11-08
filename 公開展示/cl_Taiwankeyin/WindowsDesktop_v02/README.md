# CELL 臺灣注音｜Windows v0.2 Desktop Preview

取代先前只有 R1/R2 命令列驗證的舊 Windows「第一版展示內容」：現有 **可實際執行的 Windows 圖形文字工作台**，完整 158,905 筆離線字詞、標準大千 37 鍵、免聲調連續注音組字、候選選字、字詞接續建議、簡單配色切換、文字複製至系統剪貼簿。Windows 上可在獨立視窗內輸入，複製到 Word、瀏覽器等編輯器。

**重要限制：** 這是 Tkinter/Python 打包為 Windows `.exe` 的獨立**預覽文字工作台**，尚未註冊 Windows TSF Input Method，**不能直接取代 Windows 系統輸入法**；也尚未和既有 R1 C++ SQLite 個人選字資料打通。原 R1/R2 C++ 已驗證核心保留，TSF 注冊/安裝器和 C++ 原生鏈下一關另行整合。

編譯：Windows runner 安裝 PyInstaller，`pyinstaller --noconfirm --windowed --onedir --name CELL_TaiwanKeyin_WinPreview --add-data "full_zhuyin_mobile.sqlite3;." app.py`。

程式採固定 `chewing/libchewing-data` 正體索引，中文資料只在本機查詢，不使用網路權限或遠端 API。完整原始詞庫來源與版權資訊見 Android 原詞庫 manifest。勾選或自動保存個人偏好留待 TSF 正式版本。
