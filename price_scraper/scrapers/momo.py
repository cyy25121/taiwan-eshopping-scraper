import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from .base import BaseScraper

class MomoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.momoshop.com.tw/goods/GoodsDetail.jsp"
    
    def fetch_product(self, product_id):
        """抓取 MOMO 商品資訊"""
        url = f"{self.base_url}?i_code={product_id}"
        
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            product_name = soup.select_one("#osmGoodsName")
            price_element = soup.select_one(".seoPrice")
            
            return {
                "name": product_name.text.strip() if product_name else "找不到商品名稱",
                "price": price_element.text.strip() if price_element else "找不到價格資訊",
                "url": url
            }
            
        except requests.RequestException as e:
            return {
                "error": f"抓取資料時發生錯誤: {str(e)}",
                "url": url
            }
    
    def search_products(self, keyword):
        """搜尋 MOMO 商品"""
        search_url = f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={keyword}"
        
        try:
            response = self.session.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            json_script = soup.select_one('script[type="application/ld+json"]')
            if not json_script:
                return [{"error": "找不到商品資料"}]
            
            try:
                json_data = json.loads(json_script.string)
                products = []
                
                item_list = json_data.get('mainEntity', {}).get('itemListElement', [])
                
                for item in item_list:
                    product_url = item.get('url', '')
                    if product_url:
                        parsed_url = urlparse(product_url)
                        query_params = parse_qs(parsed_url.query)
                        product_id = query_params.get('i_code', [''])[0]
                        
                        if product_id:
                            products.append({
                                'id': product_id,
                                'name': item.get('name', '無商品名稱'),
                                'url': product_url
                            })
                
                return products
                
            except json.JSONDecodeError:
                return [{"error": "解析商品資料時發生錯誤"}]
            
        except requests.RequestException as e:
            return [{"error": f"搜尋時發生錯誤: {str(e)}"}] 