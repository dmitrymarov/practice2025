from opensearchpy import OpenSearch

class SearchModule:
    def __init__(self, host='localhost', port=9200, index_name='solutions', use_mock=True):
        self.use_mock = use_mock
        self.mock_data = []
        
        if use_mock:
            # Используем имитацию вместо реального OpenSearch для демонстрации
            self._load_mock_data()
        else:
            # Настройка реального подключения к OpenSearch
            self.client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=None,
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False
            )
            self.index_name = index_name
            
            # Создаем индекс, если он не существует
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(
                    index=index_name,
                    body={
                        'settings': {
                            'number_of_shards': 1,
                            'number_of_replicas': 0
                        },
                        'mappings': {
                            'properties': {
                                'id': {'type': 'keyword'},
                                'title': {'type': 'text'},
                                'content': {'type': 'text'},
                                'tags': {'type': 'keyword'}
                            }
                        }
                    }
                )
    
    def _load_mock_data(self):
        """Загружает имитационные данные для демонстрации"""
        mock_solutions = [
            {
                "id": "sol1",
                "title": "Решение проблем с Wi-Fi подключением",
                "content": "1. Перезагрузите роутер. 2. Проверьте настройки Wi-Fi на устройстве. 3. Убедитесь, что пароль вводится правильно.",
                "tags": ["wi-fi", "интернет", "сеть", "подключение"]
            },
            {
                "id": "sol2",
                "title": "Исправление проблем с электронной почтой",
                "content": "1. Проверьте подключение к интернету. 2. Убедитесь, что логин и пароль верны. 3. Очистите кэш приложения.",
                "tags": ["email", "почта", "авторизация"]
            },
            {
                "id": "sol3",
                "title": "Устранение неполадок с браузером",
                "content": "1. Очистите историю и кэш браузера. 2. Обновите браузер до последней версии. 3. Проверьте настройки интернет-соединения.",
                "tags": ["браузер", "интернет", "зависание"]
            },
            {
                "id": "sol4",
                "title": "Решение проблем с операционной системой",
                "content": "1. Перезагрузите компьютер. 2. Проверьте наличие обновлений. 3. Запустите диагностику системы.",
                "tags": ["ОС", "система", "компьютер", "обновление"]
            },
            {
                "id": "sol5",
                "title": "Устранение проблем с мобильным приложением",
                "content": "1. Переустановите приложение. 2. Очистите кэш и данные приложения. 3. Обновите приложение до последней версии.",
                "tags": ["приложение", "смартфон", "мобильный", "ошибка"]
            }
        ]
        
        self.mock_data = mock_solutions
    
    def index_document(self, doc_id, title, content, tags=None):
        """Добавить или обновить документ в индексе"""
        document = {
            'id': doc_id,
            'title': title,
            'content': content
        }
        if tags:
            document['tags'] = tags
            
        if self.use_mock:
            # Для имитации просто добавляем в массив
            for i, doc in enumerate(self.mock_data):
                if doc['id'] == doc_id:
                    self.mock_data[i] = document
                    return
            self.mock_data.append(document)
        else:
            # Для реального OpenSearch
            self.client.index(
                index=self.index_name,
                body=document,
                id=doc_id,
                refresh=True
            )
    
    def search(self, query_text, size=10):
        """Выполнить полнотекстовый поиск"""
        if self.use_mock:
            # Простая имитация поиска
            results = []
            query_lower = query_text.lower()
            
            for doc in self.mock_data:
                score = 0
                
                # Проверяем наличие ключевых слов в заголовке
                if query_lower in doc['title'].lower():
                    score += 2
                
                # Проверяем наличие ключевых слов в содержимом
                if query_lower in doc['content'].lower():
                    score += 1
                
                # Проверяем наличие ключевых слов в тегах
                if 'tags' in doc:
                    for tag in doc['tags']:
                        if query_lower in tag.lower():
                            score += 1
                            break
                
                if score > 0:
                    result = {
                        'id': doc['id'],
                        'title': doc['title'],
                        'content': doc['content'],
                        'score': score
                    }
                    results.append(result)
            
            # Сортируем результаты по релевантности
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:size]
        else:
            # Реальный поиск через OpenSearch
            query = {
                'query': {
                    'multi_match': {
                        'query': query_text,
                        'fields': ['title^2', 'content', 'tags^1.5']
                    }
                },
                'highlight': {
                    'fields': {
                        'content': {}
                    }
                }
            }
            
            response = self.client.search(
                body=query,
                index=self.index_name,
                size=size
            )
            
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'id': hit['_source']['id'],
                    'title': hit['_source']['title'],
                    'content': hit['_source']['content'],
                    'score': hit['_score']
                }
                
                if 'highlight' in hit:
                    result['highlight'] = hit['highlight']
                    
                results.append(result)
                
            return results