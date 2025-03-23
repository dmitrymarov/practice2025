import requests
from requests.exceptions import RequestException

class MediaWikiClient:
    def __init__(self, base_url, verify_ssl=True):
        """
        Инициализация клиента MediaWiki
        
        Args:
            base_url (str): Базовый URL для API MediaWiki
            verify_ssl (bool): Проверять ли SSL-сертификаты
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api.php"
        self.session = requests.Session()
        self.verify_ssl = verify_ssl
    
    def search(self, query, limit=10):
        """
        Поиск статей по ключевому слову
        
        Args:
            query (str): Поисковый запрос
            limit (int): Максимальное количество результатов
            
        Returns:
            list: Список найденных статей
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': limit
        }
        
        try:
            response = self.session.get(self.api_endpoint, params=params, verify=self.verify_ssl)
            response.raise_for_status()  # Проверяем статус ответа
            
            data = response.json()
            results = []
            
            if 'query' in data and 'search' in data['query']:
                for item in data['query']['search']:
                    result = {
                        'id': str(item['pageid']),
                        'title': item['title'],
                        'content': item.get('snippet', ''),
                        'score': 1.0  # MediaWiki не возвращает score, используем 1.0 как значение по умолчанию
                    }
                    results.append(result)
            
            return results
        except RequestException as e:
            print(f"Ошибка при поиске в MediaWiki: {str(e)}")
            return []
    
    def get_page_content(self, page_id):
        """
        Получить содержимое страницы по ID
        
        Args:
            page_id (int): ID страницы
            
        Returns:
            str: HTML-содержимое страницы
        """
        params = {
            'action': 'parse',
            'pageid': page_id,
            'format': 'json',
            'prop': 'text'
        }
        
        try:
            response = self.session.get(self.api_endpoint, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            
            data = response.json()
            if 'parse' in data and 'text' in data['parse']:
                return data['parse']['text']['*']
            
            return None
        except RequestException as e:
            print(f"Ошибка при получении содержимого страницы: {str(e)}")
            return None
    
    def login(self, username, password):
        """
        Авторизация в MediaWiki
        
        Args:
            username (str): Имя пользователя
            password (str): Пароль
            
        Returns:
            bool: Успешность авторизации
        """
        # Получение токена для логина
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.api_endpoint, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            
            data = response.json()
            if 'query' not in data or 'tokens' not in data['query'] or 'logintoken' not in data['query']['tokens']:
                return False
            
            login_token = data['query']['tokens']['logintoken']
            
            # Выполнение логина
            params = {
                'action': 'login',
                'lgname': username,
                'lgpassword': password,
                'lgtoken': login_token,
                'format': 'json'
            }
            
            response = self.session.post(self.api_endpoint, data=params, verify=self.verify_ssl)
            response.raise_for_status()
            
            data = response.json()
            return data.get('login', {}).get('result') == 'Success'
        except RequestException as e:
            print(f"Ошибка при авторизации в MediaWiki: {str(e)}")
            return False
    
    def get_page_categories(self, page_id):
        """
        Получить категории страницы
        
        Args:
            page_id (int): ID страницы
            
        Returns:
            list: Список категорий
        """
        params = {
            'action': 'query',
            'pageids': page_id,
            'prop': 'categories',
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.api_endpoint, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            
            data = response.json()
            categories = []
            
            if 'query' in data and 'pages' in data['query'] and str(page_id) in data['query']['pages']:
                page_data = data['query']['pages'][str(page_id)]
                if 'categories' in page_data:
                    categories = [cat['title'] for cat in page_data['categories']]
            
            return categories
        except RequestException as e:
            print(f"Ошибка при получении категорий: {str(e)}")
            return []