# 三市垃圾車資訊整合 V0.2.0

## 真實資料
- 新北市：官方即時 GPS，每 2 分鐘更新；GitHub 排程每 10 分鐘同步一次。
- 臺中市：官方動態車輛，官方更新頻率約 10 分鐘。
- 臺北市：官方清運點位、路線與表定時間，不是即時 GPS。

## 啟用
1. 全部檔案上傳到 GitHub Repository 根目錄。
2. Settings > Actions > General，Workflow permissions 選 Read and write permissions。
3. Actions > Sync official garbage data > Run workflow，先手動執行一次。
4. Settings > Pages，選 Deploy from a branch、main、/(root)。
5. 等待 Pages 網址產生。

資料同步失敗時不會用假資料替代，會保留上次成功檔並在畫面顯示錯誤或過期。
