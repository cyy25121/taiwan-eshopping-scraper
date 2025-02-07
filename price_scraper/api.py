"""
電商價格爬蟲 API 模組

此模組提供 RESTful API 介面，用於：
1. 在多個電商平台搜尋商品
2. 爬取特定商品頁面的價格資訊
3. 追蹤非同步爬蟲任務的狀態
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from .worker import scrape_product_task
from enum import Enum
from urllib.parse import quote
from .scrapers.pchome import PChomeScraper
from .scrapers.momo import MomoScraper
from .models import get_db, TaskResult
import json

app = FastAPI(
    title="Price Scraper API",
    description="電商價格爬蟲 API，支援 PChome 和 Momo 平台的商品搜尋與價格追蹤",
    version="1.0.0"
)

class ECommerce(str, Enum):
    """支援的電商平台列舉"""
    PCHOME = "pchome"
    MOMO = "momo"
    ALL = "all"

class SearchRequest(BaseModel):
    """搜尋請求模型"""
    keyword: str  # 搜尋關鍵字
    platforms: List[ECommerce] = [ECommerce.ALL]  # 目標平台，預設搜尋所有平台
    notify_email: Optional[str] = None  # 可選的通知 email

class ScrapeRequest(BaseModel):
    urls: List[HttpUrl]
    notify_email: Optional[str] = None

class ScrapeResponse(BaseModel):
    task_id: str
    message: str

class SearchResult(BaseModel):
    platform: str
    products: List[dict]

@app.post("/search", response_model=ScrapeResponse)
async def search_products(request: SearchRequest, db: Session = Depends(get_db)):
    """
    非同步搜尋商品
    
    Args:
        request: 包含關鍵字和目標平台的搜尋請求
        db: 資料庫連線 session
        
    Returns:
        包含任務 ID 的回應物件
        
    Raises:
        HTTPException: 當搜尋過程發生錯誤時
    """
    try:
        # 根據選擇的平台生成搜尋 URL
        urls = []
        platforms = [p for p in ECommerce if p != ECommerce.ALL] if ECommerce.ALL in request.platforms else request.platforms
        
        encoded_keyword = quote(request.keyword)
        for platform in platforms:
            if platform == ECommerce.PCHOME:
                # PChome 搜尋 URL
                url = f"https://24h.pchome.com.tw/search?q={encoded_keyword}"
                urls.append(url)
            elif platform == ECommerce.MOMO:
                # Momo 搜尋 URL
                url = f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={encoded_keyword}"
                urls.append(url)

        # 創建爬蟲任務
        task = scrape_product_task.delay(urls, request.notify_email)
        
        # 將任務資訊存入資料庫
        db_task = TaskResult(
            id=task.id,
            status="PENDING",
            result=None
        )
        db.add(db_task)
        db.commit()
        
        return ScrapeResponse(
            task_id=task.id,
            message=f"開始在 {', '.join([p.value for p in platforms])} 搜尋 '{request.keyword}'"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/search/sync", response_model=List[SearchResult])
async def search_products_sync(request: SearchRequest):
    """
    同步搜尋商品
    
    此端點會同步執行搜尋，可能需要較長時間才會回應
    建議用於測試或少量搜尋
    
    Args:
        request: 包含關鍵字和目標平台的搜尋請求
        
    Returns:
        各平台的搜尋結果列表
    """
    try:
        results = []
        platforms = [p for p in ECommerce if p != ECommerce.ALL] if ECommerce.ALL in request.platforms else request.platforms
        
        pchome_scraper = PChomeScraper()
        momo_scraper = MomoScraper()
        
        for platform in platforms:
            if platform == ECommerce.PCHOME:
                products = pchome_scraper.search_products(request.keyword)
                results.append(SearchResult(
                    platform="pchome",
                    products=products
                ))
            elif platform == ECommerce.MOMO:
                products = momo_scraper.search_products(request.keyword)
                results.append(SearchResult(
                    platform="momo",
                    products=products
                ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_products(request: ScrapeRequest):
    try:
        task = scrape_product_task.delay([str(url) for url in request.urls], request.notify_email)
        return ScrapeResponse(
            task_id=task.id,
            message="爬蟲任務已開始執行"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    try:
        # 從資料庫查詢任務狀態
        db_task = db.query(TaskResult).filter(TaskResult.id == task_id).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # 如果資料庫中的狀態不是完成狀態，則檢查 Celery 任務狀態
        if db_task.status not in ["SUCCESS", "FAILURE"]:
            task = scrape_product_task.AsyncResult(task_id)
            if task.ready():
                # 更新資料庫中的任務狀態和結果
                db_task.status = task.status
                db_task.result = task.result
                db.commit()
        
        return {
            "task_id": task_id,
            "status": db_task.status,
            "result": db_task.result
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close() 