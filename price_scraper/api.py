from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from .worker import scrape_product_task
from enum import Enum
from urllib.parse import quote
from .scrapers.pchome import PChomeScraper
from .scrapers.momo import MomoScraper

app = FastAPI(title="Price Scraper API")

class ECommerce(str, Enum):
    PCHOME = "pchome"
    MOMO = "momo"
    ALL = "all"

class SearchRequest(BaseModel):
    keyword: str
    platforms: List[ECommerce] = [ECommerce.ALL]
    notify_email: Optional[str] = None

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
async def search_products(request: SearchRequest):
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
        return ScrapeResponse(
            task_id=task.id,
            message=f"開始在 {', '.join([p.value for p in platforms])} 搜尋 '{request.keyword}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/sync", response_model=List[SearchResult])
async def search_products_sync(request: SearchRequest):
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
async def get_task_status(task_id: str):
    task = scrape_product_task.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    } 