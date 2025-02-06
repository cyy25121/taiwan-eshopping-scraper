from celery import Celery
from typing import List, Optional
from .scrapers.pchome import PChomeScraper
from .scrapers.momo import MomoScraper
import os

# 使用環境變數獲取 Redis 連接資訊
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'price_scraper',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery_app.task(name="scrape_product")
def scrape_product_task(urls: List[str], notify_email: Optional[str] = None):
    results = []
    pchome_scraper = PChomeScraper()
    momo_scraper = MomoScraper()
    
    for url in urls:
        try:
            if "pchome" in url.lower():
                if "search" in url.lower():
                    # 搜尋模式
                    keyword = url.split("q=")[-1]
                    result = pchome_scraper.search_products(keyword)
                else:
                    # 單一商品模式
                    product_id = url.split("/prod/")[-1]
                    result = pchome_scraper.fetch_product(product_id)
            elif "momo" in url.lower():
                if "search" in url.lower():
                    # 搜尋模式
                    keyword = url.split("keyword=")[-1]
                    result = momo_scraper.search_products(keyword)
                else:
                    # 單一商品模式
                    product_id = url.split("i_code=")[-1]
                    result = momo_scraper.fetch_product(product_id)
            else:
                result = {"error": f"不支援的網站: {url}"}
            
            results.append({
                "url": url,
                "data": result
            })
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })
    
    # TODO: 如果提供 email，發送結果通知
    
    return results 