import pytest
import requests
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
import sys
import os

# 添加主程式目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import create_connection, fetch_pchome_product, search_pchome_products

def test_create_connection():
    """測試建立連線功能"""
    session, headers = create_connection()
    
    # 驗證回傳值的型別
    assert isinstance(session, requests.Session)
    assert isinstance(headers, dict)
    
    # 驗證 headers 是否包含必要的欄位
    assert 'User-Agent' in headers
    assert 'Accept' in headers
    assert 'Accept-Language' in headers

@patch('requests.Session')
def test_fetch_pchome_product_success(mock_session):
    """測試成功抓取商品資訊的情況"""
    # 模擬成功的 HTTP 回應
    mock_response = Mock()
    mock_response.text = '''
        <html>
            <div class="o-prodMainName">測試商品</div>
            <div class="o-prodPrice__price">1000</div>
        </html>
    '''
    mock_response.raise_for_status.return_value = None
    mock_session.return_value.get.return_value = mock_response
    
    # 執行測試
    result = fetch_pchome_product('TEST-123')
    
    # 驗證結果
    assert result['name'] == '測試商品'
    assert result['price'] == '1000'
    assert result['url'] == 'https://24h.pchome.com.tw/prod/TEST-123'

@patch('requests.Session')
def test_fetch_pchome_product_failure(mock_session):
    """測試抓取商品資訊失敗的情況"""
    # 模擬請求失敗
    mock_session.return_value.get.side_effect = requests.RequestException('測試錯誤')
    
    # 執行測試
    result = fetch_pchome_product('TEST-123')
    
    # 驗證結果
    assert 'error' in result
    assert '測試錯誤' in result['error']

@patch('requests.Session')
def test_search_pchome_products_success(mock_session):
    """測試成功搜尋商品的情況"""
    # 模擬成功的 HTTP 回應
    mock_response = Mock()
    mock_response.text = '''
        <html>
            <a class="c-prodInfoV2__link" href="/prod/TEST-123">
                <div class="c-prodInfoV2__title">測試商品1</div>
            </a>
            <a class="c-prodInfoV2__link" href="/prod/TEST-456">
                <div class="c-prodInfoV2__title">測試商品2</div>
            </a>
        </html>
    '''
    mock_response.raise_for_status.return_value = None
    mock_session.return_value.get.return_value = mock_response
    
    # 執行測試
    results = search_pchome_products('測試關鍵字')
    
    # 驗證結果
    assert len(results) == 2
    assert results[0]['id'] == 'TEST-123'
    assert results[0]['name'] == '測試商品1'
    assert results[1]['id'] == 'TEST-456'
    assert results[1]['name'] == '測試商品2'

@patch('requests.Session')
def test_search_pchome_products_failure(mock_session):
    """測試搜尋商品失敗的情況"""
    # 模擬請求失敗
    mock_session.return_value.get.side_effect = requests.RequestException('測試錯誤')
    
    # 執行測試
    results = search_pchome_products('測試關鍵字')
    
    # 驗證結果
    assert len(results) == 1
    assert 'error' in results[0]
    assert '測試錯誤' in results[0]['error'] 