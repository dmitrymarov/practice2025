import logging
import json
import requests
import re
from opensearchpy import OpenSearch, ConnectionError, NotFoundError, RequestError

logger = logging.getLogger(__name__)

class SearchModule:
    def __init__(self, host='localhost', port=9200, index_name='solutions', use_mock=True):
        self.use_mock = use_mock
        self.mock_data = []
        self.host = host
        self.port = port
        self.index_name = index_name
        
        if use_mock:
            # Используем имитацию вместо реального OpenSearch для демонстрации
            logger.info("Инициализация с использованием мок-данных")
            self._load_mock_data()
        else:
            logger.info(f"Попытка подключения к OpenSearch: {host}:{port}")
            try:
                self.client = OpenSearch(
                    hosts=[{'host': host, 'port': port}],
                    http_auth=None,
                    use_ssl=False,
                    verify_certs=False,
                    ssl_show_warn=False,
                    timeout=30,
                    retry_on_timeout=True,
                    max_retries=3
                )
                if not self.client.ping():
                    raise ConnectionError("Не удалось установить соединение с OpenSearch")
                logger.info("Подключение к OpenSearch успешно установлено")
                if not self.client.indices.exists(index=index_name):
                    logger.info(f"Создание индекса {index_name}")
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
                    logger.info(f"Индекс {index_name} успешно создан")
                else:
                    logger.info(f"Индекс {index_name} уже существует")
                try:
                    count = self.client.count(index=index_name)
                    logger.info(f"Количество документов в индексе: {count.get('count', 0)}")
                    if count.get('count', 0) == 0:
                        logger.info("Индекс пуст, добавляем демо-данные")
                        self._load_mock_data()
                        for doc in self.mock_data:
                            self.index_document(
                                doc_id=doc['id'],
                                title=doc['title'],
                                content=doc['content'],
                                tags=doc.get('tags', [])
                            )
                        logger.info(f"Демо-данные ({len(self.mock_data)} записей) добавлены в индекс")
                except Exception as e:
                    logger.error(f"Ошибка при проверке содержимого индекса: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Ошибка при подключении к OpenSearch: {str(e)}")
                logger.info("Использование режима моков из-за ошибки подключения")
                self.use_mock = True
                self._load_mock_data()
    
    def _load_mock_data(self):
        """Загружает имитационные данные для демонстрации"""
        mock_solutions = [
            {
                "id": "sol1",
                "title": "Решение проблем с Wi-Fi подключением",
                "content": "1. Перезагрузите роутер. 2. Проверьте настройки Wi-Fi на устройстве. 3. Убедитесь, что пароль вводится правильно.",
                "tags": ["wi-fi", "интернет", "сеть", "подключение"],
                "source": "mock"
            },
            {
                "id": "sol2",
                "title": "Исправление проблем с электронной почтой",
                "content": "1. Проверьте подключение к интернету. 2. Убедитесь, что логин и пароль верны. 3. Очистите кэш приложения.",
                "tags": ["email", "почта", "авторизация"],
                "source": "mock"
            },
            {
                "id": "sol3",
                "title": "Устранение неполадок с браузером",
                "content": "1. Очистите историю и кэш браузера. 2. Обновите браузер до последней версии. 3. Проверьте настройки интернет-соединения.",
                "tags": ["браузер", "интернет", "зависание"],
                "source": "mock"
            },
            {
                "id": "sol4",
                "title": "Решение проблем с операционной системой",
                "content": "1. Перезагрузите компьютер. 2. Проверьте наличие обновлений. 3. Запустите диагностику системы.",
                "tags": ["ОС", "система", "компьютер", "обновление"],
                "source": "mock"
            },
            {
                "id": "sol5",
                "title": "Устранение проблем с мобильным приложением",
                "content": "1. Переустановите приложение. 2. Очистите кэш и данные приложения. 3. Обновите приложение до последней версии.",
                "tags": ["приложение", "смартфон", "мобильный", "ошибка"],
                "source": "mock"
            }
        ]
        
        self.mock_data = mock_solutions
        logger.info(f"Загружено {len(self.mock_data)} мок-записей")
    
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
                    logger.info(f"Обновлен мок-документ: {doc_id}")
                    return
            self.mock_data.append(document)
            logger.info(f"Добавлен мок-документ: {doc_id}")
        else:
            try:
                self.client.index(
                    index=self.index_name,
                    body=document,
                    id=doc_id,
                    refresh=True
                )
                logger.info(f"Документ успешно проиндексирован в OpenSearch: {doc_id}")
            except Exception as e:
                logger.error(f"Ошибка при индексации документа {doc_id}: {str(e)}")
    
    def search_mediawiki(self, query_text, base_url=None, limit=5):
        """Выполнить поиск в MediaWiki API"""
        if not base_url:
            logger.debug("URL MediaWiki не указан, поиск пропущен")
            return []
        try:
            api_url = f"{base_url}/api.php"
            logger.info(f"Поиск в MediaWiki: {api_url}?search={query_text}")
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query_text,
                'format': 'json',
                'srlimit': limit
            }
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Ошибка при запросе к MediaWiki API: {response.status_code}")
                return []
                
            data = response.json()
            
            # Обрабатываем результаты поиска
            results = []
            if 'query' in data and 'search' in data['query']:
                for item in data['query']['search']:
                    # Создаем объект результата
                    result = {
                        'id': f"mediawiki_{item['pageid']}",
                        'title': item['title'],
                        'content': self._clean_html(item.get('snippet', '')),
                        'score': 1.0,  # MediaWiki не возвращает оценку релевантности
                        'source': 'mediawiki',
                        'url': f"{base_url}/index.php?curid={item['pageid']}"
                    }
                    results.append(result)
            
            logger.info(f"Найдено {len(results)} результатов в MediaWiki")
            return results
        
        except Exception as e:
            logger.error(f"Ошибка при поиске в MediaWiki: {str(e)}")
            return []
    
    def _clean_html(self, html_text):
        """Очистка HTML-разметки из текста"""
        clean_text = re.sub(r'<[^>]+>', ' ', html_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def search(self, query_text, size=10, mediawiki_url=None):
        """Выполнить полнотекстовый поиск из всех источников"""
        all_results = []
        logger.info(f"Поисковый запрос: '{query_text}'")
        
        # 1. Поиск в мок-данных (если включен режим моков)
        if self.use_mock:
            logger.info("Выполняем поиск в мок-данных...")
            mock_results = self._search_mock(query_text)
            for result in mock_results:
                result['source'] = 'mock'
            all_results.extend(mock_results)
        
        # 2. Поиск в OpenSearch (если не используем моки)
        else:
            try:
                opensearch_results = self._search_opensearch(query_text, size)
                for result in opensearch_results:
                    result['source'] = 'opensearch'
                all_results.extend(opensearch_results)
            except Exception as e:
                logger.error(f"Ошибка при поиске в OpenSearch: {str(e)}")
                logger.info("Используем мок-данные из-за ошибки OpenSearch")
                mock_results = self._search_mock(query_text)
                for result in mock_results:
                    result['source'] = 'mock'
                all_results.extend(mock_results)
        
        # 3. Поиск в MediaWiki (если указан URL)
        if mediawiki_url:
            logger.info(f"Выполняем поиск в MediaWiki по URL: {mediawiki_url}")
            try:
                mediawiki_results = self.search_mediawiki(query_text, mediawiki_url)
                all_results.extend(mediawiki_results)
            except Exception as e:
                logger.error(f"Ошибка при поиске в MediaWiki: {str(e)}")
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        logger.info(f"Найдено {len(all_results)} результатов")
        return all_results[:size]
    
    def _search_mock(self, query_text):
        """Поиск в мок-данных"""
        results = []
        query_lower = query_text.lower()
        
        for doc in self.mock_data:
            score = 0
            if query_lower in doc['title'].lower():
                score += 2
            if query_lower in doc['content'].lower():
                score += 1
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
                    'score': score,
                    'source': doc.get('source', 'mock')
                }
                results.append(result)
        results.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"Найдено {len(results)} результатов в мок-данных")
        return results
    
    def _search_opensearch(self, query_text, size=10):
        """Поиск в OpenSearch"""
        try:
            query = {
                'query': {
                    'multi_match': {
                        'query': query_text,
                        'fields': ['title^2', 'content', 'tags^1.5'],
                        'type': 'best_fields'
                    }
                },
                'highlight': {
                    'fields': {
                        'content': {}
                    }
                }
            }
            logger.info(f"Поисковый запрос к OpenSearch: {json.dumps(query)}")
            response = self.client.search(
                index=self.index_name,
                body=query,
                size=size
            )
            results = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                result = {
                    'id': source.get('id', hit['_id']),
                    'title': source.get('title', 'Без названия'),
                    'content': source.get('content', ''),
                    'score': hit['_score'],
                    'source': 'opensearch',  # Принудительно указываем источник
                    'url': source.get('url', '')
                }
                if 'highlight' in hit and 'content' in hit['highlight']:
                    result['highlight'] = hit['highlight']['content'][0]
                results.append(result)
            logger.info(f"Найдено {len(results)} результатов в OpenSearch")
            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске в OpenSearch: {str(e)}")
            logger.exception("Детальная информация об ошибке:")
            return []