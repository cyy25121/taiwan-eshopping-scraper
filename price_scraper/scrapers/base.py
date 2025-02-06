from abc import ABC, abstractmethod
import requests
from ..utils import create_connection

class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    @abstractmethod
    def search_products(self, keyword):
        pass
    
    @abstractmethod
    def fetch_product(self, product_id):
        pass 