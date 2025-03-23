from flask import Flask
from app.config import Config
from app.modules.decision_graph import DecisionGraph, create_sample_graph
from app.modules.search_module import SearchModule
from app.modules.servicedesk import ServiceDeskModule
import os

# Инициализируем глобальные объекты
decision_graph = None
search_module = None
service_desk = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация модулей
    init_modules(app)
    
    # Регистрация маршрутов
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app

def init_modules(app):
    global decision_graph, search_module, service_desk
    
    # Инициализация графа решений
    if os.path.exists(app.config['GRAPH_DATA_FILE']):
        decision_graph = DecisionGraph.load_from_file(app.config['GRAPH_DATA_FILE'])
    else:
        # Создаем пример графа
        decision_graph = create_sample_graph()
        decision_graph.save_to_file(app.config['GRAPH_DATA_FILE'])
    
    # Инициализация модуля поиска
    search_module = SearchModule(
        host=app.config['OPENSEARCH_HOST'],
        port=app.config['OPENSEARCH_PORT'],
        index_name=app.config['OPENSEARCH_INDEX'],
        use_mock=app.config['USE_MOCK_SERVICES']
    )
    
    # Инициализация модуля Service Desk
    service_desk = ServiceDeskModule(
        api_url=app.config['SERVICEDESK_URL'],
        api_key=app.config['SERVICEDESK_API_KEY'],
        use_mock=app.config['USE_MOCK_SERVICES']
    )