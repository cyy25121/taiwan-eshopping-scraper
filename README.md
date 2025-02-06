# 台灣電商商品爬蟲服務
這是一個用於抓取 MOMO 和 PChome 商品價格的爬蟲系統。
此為個人練習，僅供學習使用。

## 系統功能
- 支援 MOMO 和 PChome 兩大電商平台
- 可搜尋商品並取得價格資訊
- 提供同步和非同步 API 介面
- 使用 Celery 處理非同步任務
- 支援 Docker 容器化部署

## 技術需求
- Python 3.12+
- Redis
- Docker 和 Docker Compose (選用)

## 安裝方式 
使用 pip 安裝相依套件：
```bash
pip install -r requirements.txt
```
使用 Docker Compose 啟動服務：
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
curl -X POST "http://localhost:8000/search" -H "Content-Type: application/json" -d '{"keyword": "口罩", "platforms": ["all"]}'
```
爬取特定商品：
```bash
curl -X POST "http://localhost:8000/scrape" -H "Content-Type: application/json" -d '{"urls": ["https://24h.pchome.com.tw/prod/PRODUCT_ID"]}'
```

## 更新紀錄
- v0.0.1 初始版本

## 待完成

### 爬蟲
- 資料清洗
- 錯誤處理

### API
- 搜尋方法定義

## 其他
授權：本專案採用 MIT 授權條款。
