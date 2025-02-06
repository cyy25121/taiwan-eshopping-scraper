import pytest
from unittest.mock import Mock, patch
from price_scraper import PChomeScraper
import requests

@pytest.fixture
def pchome_scraper():
    """建立 PChomeScraper 實例的 fixture"""
    return PChomeScraper()

@patch('requests.Session')
def test_fetch_product_success(mock_session, pchome_scraper):
    """測試成功抓取商品資訊的情況"""
    mock_response = Mock()
    mock_response.text = '''
        <div class="o-prodMainName">測試商品</div>
        <div class="o-prodPrice__price">1000</div>
    '''
    
    # 設定 mock session
    mock_session.return_value.get.return_value = mock_response
    
    # 替換 pchome_scraper 的 session
    pchome_scraper.session = mock_session()
    
    result = pchome_scraper.fetch_product('TEST-123')
    
    assert result['name'] == '測試商品'
    assert result['price'] == '1000'

@patch('requests.Session')
def test_fetch_product_failure(mock_session, pchome_scraper):
    """測試抓取商品資訊失敗的情況"""
    # 設定 mock session 會拋出 requests.RequestException
    mock_session.return_value.get.side_effect = requests.RequestException('測試錯誤')
    
    # 替換 pchome_scraper 的 session
    pchome_scraper.session = mock_session()
    
    result = pchome_scraper.fetch_product('TEST-123')
    
    assert 'error' in result
    assert '測試錯誤' in result['error']

@patch('requests.Session')
def test_search_products_success(mock_session, pchome_scraper):
    """測試成功搜尋商品的情況"""
    mock_response = Mock()
    mock_response.text = '''
        <a class="c-prodInfoV2__link" href="/prod/TEST-123">
            <div class="c-prodInfoV2__title">測試商品1</div>
        </a>
        <a class="c-prodInfoV2__link" href="/prod/TEST-456">
            <div class="c-prodInfoV2__title">測試商品2</div>
        </a>
    '''
    mock_session.return_value.get.return_value = mock_response
    
    # 替換 pchome_scraper 的 session
    pchome_scraper.session = mock_session()
    
    results = pchome_scraper.search_products('測試關鍵字')
    
    assert len(results) == 2
    assert results[0]['name'] == '測試商品1'
    assert results[1]['name'] == '測試商品2' 