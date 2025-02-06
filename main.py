from price_scraper import MomoScraper, PChomeScraper

# 使用 MOMO 爬蟲
momo = MomoScraper()
results = momo.search_products("口罩")
for product in results:
    if "error" not in product:
        detail = momo.fetch_product(product['id'])
        print(f"商品名稱: {detail['name']}")
        print(f"商品價格: {detail['price']}")
        print("-" * 50)

# 使用 PChome 爬蟲
pchome = PChomeScraper()
results = pchome.search_products("口罩")
# ... 類似的處理邏輯