# 台灣電商商品爬蟲服務
這是一個用於抓取 MOMO 和 PChome 商品價格的爬蟲系統。
此為個人練習，僅供學習使用。

## 系統功能
- 支援 MOMO 和 PChome 兩大電商平台
- 可搜尋商品並取得價格資訊
- 提供同步和非同步 API 介面
- 使用 Celery 處理非同步任務
- 支援 Docker 容器化部署
- 使用 PostgreSQL 儲存任務狀態
- 完整的單元測試覆蓋

## 技術需求
- Python 3.12+
- Redis (用於 Celery 任務佇列)
- PostgreSQL (用於儲存任務狀態)
- Docker 和 Docker Compose (建議使用)

## 安裝方式

### 使用 Docker Compose
```bash
docker-compose up -d
```


## API 端點
1. POST /search
- 非同步搜尋商品
- 參數：
  - keyword: 搜尋關鍵字
  - platforms: 要搜尋的平台 (pchome/momo/all)
  - notify_email: 通知信箱 (選填)

2. POST /search/sync
- 同步搜尋商品
- 參數同上

3. POST /scrape
- 爬取指定商品網址
- 參數：
  - urls: 商品網址列表
  - notify_email: 通知信箱 (選填)

4. GET /task/{task_id}
- 查詢非同步任務狀態
- 參數：
  - task_id: 任務 ID

## 使用範例
搜尋商品：
```bash
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "口罩", "platforms": ["all"]}'
```
爬取特定商品：
```bash
curl -X POST "http://localhost:8000/scrape" \
     -H "Content-Type: application/json" \
      -d '{"urls": ["https://24h.pchome.com.tw/prod/PRODUCT_ID"]}'
```
查詢任務狀態：
```bash
curl "http://localhost:8000/task/TASK_ID"
```
## 開發工具
- pgAdmin: http://localhost:5050 (預設帳密：admin@admin.com/admin)

## 測試
執行單元測試：
```bash
pytest tests/
```

## 更新紀錄
- v0.1.0
  - 新增非同步搜尋功能
- v0.0.1 初始版本

## 待完成
- 資料清洗和格式標準化
- 錯誤處理機制強化
- 搜尋結果排序和過濾
- 商品價格追蹤功能
- API 文件完善
- 效能優化

## 授權
本專案採用 MIT 授權條款。
