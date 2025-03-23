from flask import Flask
from app.config import Config
from app.modules.decision_graph import DecisionGraph, create_sample_graph
from app.modules.search_module import SearchModule
from app.modules.servicedesk import ServiceDeskModule
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализируем глобальные объекты
decision_graph = None
search_module = None
service_desk = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация модулей
    init_modules(app)
    
    # Регистрация основных маршрутов
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Добавляем Swagger UI
    add_swagger_ui(app)
    
    return app

def init_modules(app):
    global decision_graph, search_module, service_desk
    
    # Инициализация графа решений
    if os.path.exists(app.config['GRAPH_DATA_FILE']):
        logger.info(f"Загружаем граф решений из файла {app.config['GRAPH_DATA_FILE']}")
        decision_graph = DecisionGraph.load_from_file(app.config['GRAPH_DATA_FILE'])
    else:
        # Создаем пример графа
        logger.info("Создаем пример графа решений")
        decision_graph = create_sample_graph()
        decision_graph.save_to_file(app.config['GRAPH_DATA_FILE'])
    
    # Инициализация модуля поиска (обратите внимание на правильные имена параметров)
    logger.info("Инициализация модуля поиска")
    search_module = SearchModule(
        host=app.config['OPENSEARCH_HOST'],  # Было opensearch_host
        port=app.config['OPENSEARCH_PORT'],  # Было opensearch_port
        index_name=app.config['OPENSEARCH_INDEX'],
        use_mock=app.config['USE_MOCK_SERVICES']
    )
    
    # Инициализация модуля Service Desk
    logger.info("Инициализация модуля Service Desk")
    service_desk = ServiceDeskModule(
        api_url=app.config['SERVICEDESK_URL'],
        api_key=app.config['SERVICEDESK_API_KEY'],
        use_mock=app.config['USE_MOCK_SERVICES']
    )

def add_swagger_ui(app):
    """Добавление Swagger UI к приложению Flask"""
    logger.info("Инициализация Swagger UI")
    
    # Импортируем модули Swagger
    from app.swagger import swagger_blueprint, api_spec_blueprint, register_api_routes
    
    # Регистрируем блюпринты Swagger
    app.register_blueprint(swagger_blueprint)
    app.register_blueprint(api_spec_blueprint)
    
    # Регистрируем маршруты API в спецификации Swagger
    with app.app_context():
        register_api_routes(app)
        
    # Добавляем редирект с /api к документации
    @app.route('/api')
    def api_redirect():
        from flask import redirect
        return redirect('/api/docs')
        
    logger.info("Swagger UI успешно инициализирован")