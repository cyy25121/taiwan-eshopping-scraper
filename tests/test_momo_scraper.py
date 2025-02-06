import pytest
from unittest.mock import Mock, patch
from price_scraper import MomoScraper
import requests

@pytest.fixture
def momo_scraper():
    """建立 MomoScraper 實例的 fixture"""
    return MomoScraper()

@patch('requests.Session')
def test_fetch_product_success(mock_session, momo_scraper):
    """測試成功抓取商品資訊的情況"""
    mock_response = Mock()
    mock_response.text = '<html><span id="osmGoodsName">測試商品</span><span class="seoPrice">1000</span></html>'
    
    # 設定 mock session
    mock_session.return_value.get.return_value = mock_response
    
    # 替換 momo_scraper 的 session
    momo_scraper.session = mock_session()
    
    result = momo_scraper.fetch_product('8531744')
    
    assert result['name'] == '測試商品'
    assert result['price'] == '1000'

@patch('requests.Session')
def test_fetch_product_failure(mock_session, momo_scraper):
    """測試抓取商品資訊失敗的情況"""
    # 設定 mock session
    mock_session.return_value.get.side_effect = requests.RequestException('測試錯誤')
    
    # 替換 momo_scraper 的 session
    momo_scraper.session = mock_session()
    
    result = momo_scraper.fetch_product('8531744')
    
    assert 'error' in result

@patch('requests.Session')
def test_search_products_success(mock_session, momo_scraper):
    """測試成功搜尋商品的情況"""
    mock_response = Mock()
    mock_response.text = '''
        <script type="application/ld+json">
        {"mainEntity": {"itemListElement": [
            {"url": "https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=8531744", "name": "測試商品1"},
            {"url": "https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=8531745", "name": "測試商品2"}
        ]}}
        </script>
    '''
    # 設定 mock session
    mock_session.return_value.get.return_value = mock_response
    
    # 替換 momo_scraper 的 session
    momo_scraper.session = mock_session()
    
    results = momo_scraper.search_products('測試關鍵字')
    
    assert len(results) == 2
    assert results[0]['name'] == '測試商品1'
    assert results[1]['name'] == '測試商品2' 