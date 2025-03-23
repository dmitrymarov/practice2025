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
    
    # Настройки Service Desk
    SERVICEDESK_URL = os.environ.get('SERVICEDESK_URL')
    SERVICEDESK_API_KEY = os.environ.get('SERVICEDESK_API_KEY')
    
    # Настройки приложения
    GRAPH_DATA_FILE = os.environ.get('GRAPH_DATA_FILE') or 'graph_data.json'
    USE_MOCK_SERVICES = os.environ.get('USE_MOCK_SERVICES', 'True').lower() == 'true'