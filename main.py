import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urlparse, parse_qs

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def create_connection():
    """
    建立連線所需的共用設定
    
    Returns:
        tuple: (session物件, headers字典)
    """
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    session = requests.Session()
    time.sleep(random.uniform(1, 3))
    
    return session, headers

def fetch_pchome_product(product_id, connection=None):
    """
    抓取 PChome 商品資訊
    
    Args:
        product_id (str): 商品ID，例如 'DCAS86-1900GQ7X5'
        connection (tuple, optional): (session, headers) 元組，如果沒有提供則建立新的
    
    Returns:
        dict: 包含商品名稱和價格的字典，如果抓取失敗則返回相應的錯誤訊息
    """
    base_url = "https://24h.pchome.com.tw/prod/"
    url = base_url + product_id
    
    if connection is None:
        session, headers = create_connection()
    else:
        session, headers = connection
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # 檢查請求是否成功
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 抓取商品名稱
        product_name = soup.select_one(".o-prodMainName")
        
        # 抓取商品價格
        price_element = soup.select_one(".o-prodPrice__price")
        
        result = {
            "name": product_name.text.strip() if product_name else "找不到商品名稱",
            "price": price_element.text.strip() if price_element else "找不到價格資訊",
            "url": url
        }
        
        return result
        
    except requests.RequestException as e:
        return {
            "error": f"抓取資料時發生錯誤: {str(e)}",
            "url": url
        }

def search_pchome_products(keyword, connection=None):
    """
    搜尋 PChome 商品
    
    Args:
        keyword (str): 搜尋關鍵字
        connection (tuple, optional): (session, headers) 元組，如果沒有提供則建立新的
    
    Returns:
        list: 包含商品資訊的列表，每個商品包含 ID、名稱和連結
    """
    search_url = f"https://24h.pchome.com.tw/search/?q={keyword}"
    
    if connection is None:
        session, headers = create_connection()
    else:
        session, headers = connection
    
    try:
        response = session.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 找到所有商品連結
        products_container = soup.select(".c-prodInfoV2__link")
        
        products = []
        for product in products_container:
            product_url = product.get('href', '')
            if product_url:
                # 從 URL 中提取商品 ID（移除開頭的 /prod/）
                product_id = product_url.replace('/prod/', '')
                # 找到商品名稱
                product_name = product.select_one('.c-prodInfoV2__title')
                
                products.append({
                    'id': product_id,
                    'name': product_name.text.strip() if product_name else "無商品名稱",
                    'url': f"https://24h.pchome.com.tw/prod/{product_id}"
                })
        
        return products
        
    except requests.RequestException as e:
        return [{"error": f"搜尋時發生錯誤: {str(e)}"}]

def fetch_momo_product(product_id, connection=None):
    """
    抓取 MOMO 商品資訊
    
    Args:
        product_id (str): 商品ID，例如 '8531744'
        connection (tuple, optional): (session, headers) 元組，如果沒有提供則建立新的
    
    Returns:
        dict: 包含商品名稱和價格的字典，如果抓取失敗則返回相應的錯誤訊息
    """
    base_url = "https://www.momoshop.com.tw/goods/GoodsDetail.jsp"
    url = f"{base_url}?i_code={product_id}"
    
    if connection is None:
        session, headers = create_connection()
    else:
        session, headers = connection
    
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 抓取商品名稱
        product_name = soup.select_one("#osmGoodsName")
        
        # 抓取商品價格
        price_element = soup.select_one(".seoPrice")
        
        result = {
            "name": product_name.text.strip() if product_name else "找不到商品名稱",
            "price": price_element.text.strip() if price_element else "找不到價格資訊",
            "url": url
        }
        
        return result
        
    except requests.RequestException as e:
        return {
            "error": f"抓取資料時發生錯誤: {str(e)}",
            "url": url
        }

def search_momo_products(keyword, connection=None):
    """
    搜尋 MOMO 商品
    
    Args:
        keyword (str): 搜尋關鍵字
        connection (tuple, optional): (session, headers) 元組，如果沒有提供則建立新的
    
    Returns:
        list: 包含商品資訊的列表，每個商品包含 ID、名稱和連結
    """
    search_url = f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={keyword}"
    
    if connection is None:
        session, headers = create_connection()
    else:
        session, headers = connection
    
    try:
        response = session.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 找到 JSON 資料
        json_script = soup.select_one('script[type="application/ld+json"]')
        if not json_script:
            return [{"error": "找不到商品資料"}]
        
        try:
            import json
            json_data = json.loads(json_script.string)
            products = []
            
            # 從 mainEntity.itemListElement 取得商品列表
            item_list = json_data.get('mainEntity', {}).get('itemListElement', [])
            
            for item in item_list:
                product_url = item.get('url', '')
                if product_url:
                    # 從 URL 中提取商品 ID
                    from urllib.parse import urlparse, parse_qs
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

if __name__ == "__main__":
    connection = create_connection()
    
    keyword = "口罩"
    search_results = search_momo_products(keyword, connection)
    print(search_results)
    
    if search_results and "error" not in search_results[0]:
        print(f"搜尋 '{keyword}' 的結果：")
        for product in search_results:
            fetch_product = fetch_momo_product(product['id'], connection)
            print(f"商品名稱: {product['name']}")
            print(f"商品名稱: {fetch_product['name']}")
            print(f"商品價格: {fetch_product['price']}")
            print(f"商品ID: {product['id']}")
            print(f"商品連結: {product['url']}")
            print("-" * 50)
    else:
        print(search_results[0]["error"])