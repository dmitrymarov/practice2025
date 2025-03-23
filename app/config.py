import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Настройки OpenSearch
    OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST') or 'localhost'
    OPENSEARCH_PORT = int(os.environ.get('OPENSEARCH_PORT') or 9200)
    OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX') or 'solutions'
    
    # Настройки MediaWiki
    MEDIAWIKI_URL = os.environ.get('MEDIAWIKI_URL')
    MEDIAWIKI_USERNAME = os.environ.get('MEDIAWIKI_USERNAME')
    MEDIAWIKI_PASSWORD = os.environ.get('MEDIAWIKI_PASSWORD')
    USE_MEDIAWIKI = os.environ.get('USE_MEDIAWIKI', 'True').lower() == 'true'
    
    # Настройки Service Desk
    SERVICEDESK_URL = os.environ.get('SERVICEDESK_URL')
    SERVICEDESK_API_KEY = os.environ.get('SERVICEDESK_API_KEY')
    
    # Настройки приложения
    GRAPH_DATA_FILE = os.environ.get('GRAPH_DATA_FILE') or 'graph_data.json'
    USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'True').lower() == 'true'
    
    # Настройки API и Swagger
    ENABLE_SWAGGER = os.environ.get('ENABLE_SWAGGER', 'True').lower() == 'true'
    API_TITLE = "Система обработки запросов - API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API для системы обработки запросов пользователей"
    
    # Настройки безопасности
    # В продакшене рекомендуется добавить аутентификацию для API
    API_REQUIRES_AUTH = os.environ.get('API_REQUIRES_AUTH', 'False').lower() == 'true'