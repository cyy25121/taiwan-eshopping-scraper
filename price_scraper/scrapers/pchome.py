import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

class PChomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://24h.pchome.com.tw/prod/"
    
    def fetch_product(self, product_id):
        """抓取 PChome 商品資訊"""
        url = self.base_url + product_id
        
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            product_name = soup.select_one(".o-prodMainName")
            price_element = soup.select_one(".o-prodPrice__price")
            
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
        """搜尋 PChome 商品"""
        search_url = f"https://24h.pchome.com.tw/search/?q={keyword}"
        
        try:
            response = self.session.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            products_container = soup.select(".c-prodInfoV2__link")
            products = []
            
            for product in products_container:
                product_url = product.get('href', '')
                if product_url:
                    product_id = product_url.replace('/prod/', '')
                    product_name = product.select_one('.c-prodInfoV2__title')
                    
                    products.append({
                        'id': product_id,
                        'name': product_name.text.strip() if product_name else "無商品名稱",
                        'url': f"https://24h.pchome.com.tw/prod/{product_id}"
                    })
            
            return products
            
        except requests.RequestException as e:
            return [{"error": f"搜尋時發生錯誤: {str(e)}"}] 