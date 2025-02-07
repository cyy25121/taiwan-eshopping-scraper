"""
Celery 工作者模組

處理非同步爬蟲任務，支援：
1. 多平台商品搜尋
2. 單一商品資訊爬取
3. 任務結果儲存
"""

from celery import Celery
from typing import List, Optional, Dict, Any
from .scrapers.pchome import PChomeScraper
from .scrapers.momo import MomoScraper
import os
import logging
from .models import SessionLocal, TaskResult
from urllib.parse import urlparse, parse_qs

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery 配置
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'price_scraper',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

def parse_url(url: str) -> Dict[str, str]:
    """
    解析 URL 取得平台和關鍵資訊
    
    Args:
        url: 目標 URL
        
    Returns:
        包含平台和查詢參數的字典
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if "pchome" in parsed.netloc:
        platform = "pchome"
        keyword = params.get("q", [""])[0] if "search" in parsed.path else parsed.path.split("/prod/")[-1]
    elif "momo" in parsed.netloc:
        platform = "momo"
        keyword = params.get("keyword", [""])[0] if "search" in parsed.path else params.get("i_code", [""])[0]
    else:
        platform = "unknown"
        keyword = ""
        
    return {
        "platform": platform,
        "keyword": keyword,
        "is_search": "search" in parsed.path
    }

@celery_app.task(name="scrape_product")
def scrape_product_task(urls: List[str], notify_email: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    執行爬蟲任務
    
    Args:
        urls: 要爬取的 URL 列表
        notify_email: 可選的通知 email
        
    Returns:
        爬取結果列表
    """
    results = []
    scrapers = {
        "pchome": PChomeScraper(),
        "momo": MomoScraper()
    }
    
    for url in urls:
        try:
            logger.info(f"開始處理 URL: {url}")
            url_info = parse_url(url)
            
            if url_info["platform"] not in scrapers:
                raise ValueError(f"不支援的平台: {url}")
                
            scraper = scrapers[url_info["platform"]]
            if url_info["is_search"]:
                result = scraper.search_products(url_info["keyword"])
            else:
                result = scraper.fetch_product(url_info["keyword"])
                
            results.append({
                "url": url,
                "data": result
            })
            logger.info(f"成功處理 URL: {url}")
            
        except Exception as e:
            logger.error(f"處理 URL 時發生錯誤: {url}, 錯誤: {str(e)}")
            results.append({
                "url": url,
                "error": str(e)
            })
    
    try:
        # 更新資料庫狀態
        with SessionLocal() as db:
            db_task = db.query(TaskResult).filter(TaskResult.id == scrape_product_task.request.id).first()
            if db_task:
                db_task.status = "SUCCESS"
                db_task.result = results
                db.commit()
                logger.info(f"已更新任務狀態: {scrape_product_task.request.id}")
    except Exception as e:
        logger.error(f"更新資料庫狀態時發生錯誤: {str(e)}")
    
    return results 