from flask import Flask, redirect, render_template
from app.config import Config
from app.modules.decision_graph import DecisionGraph, create_sample_graph
from app.modules.search_module import SearchModule
from app.modules.servicedesk import ServiceDeskModule
import os
import logging
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
    if app.config.get('ENABLE_SWAGGER', True):
        try:
            add_swagger_ui(app)
            logger.info("Swagger UI успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Swagger UI: {str(e)}")
            logger.info("Продолжаем запуск приложения без Swagger UI")
    
# Добавляем обработчик ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error="Страница не найдена", code=404), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error="Внутренняя ошибка сервера", code=500), 500
        
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
    
    # Определяем, использовать ли моки
    use_mock = app.config.get('USE_MOCK_SERVICES', True)
    
    # Проверяем доступность OpenSearch
    if not use_mock:
        try:
            import requests
            response = requests.get(f"http://{app.config['OPENSEARCH_HOST']}:{app.config['OPENSEARCH_PORT']}", timeout=3)
            if response.status_code != 200:
                logger.warning("OpenSearch недоступен, переключаемся на моки")
                use_mock = True
        except Exception as e:
            logger.warning(f"Ошибка при проверке доступности OpenSearch: {str(e)}")
            logger.warning("Переключаемся на моки")
            use_mock = True
    
    search_module = SearchModule(
        host=app.config['OPENSEARCH_HOST'],
        port=app.config['OPENSEARCH_PORT'],
        index_name=app.config['OPENSEARCH_INDEX'],
        use_mock=use_mock
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

    try:
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
    except Exception as e:
        logger.error(f"Ошибка при инициализации Swagger UI: {str(e)}")
        # Создаем заглушку для /api при ошибке
        @app.route('/api')
        def api_error():
            from flask import jsonify
            return jsonify({
                "error": "Swagger UI не инициализирован",
                "message": "API доступно, но документация недоступна"
            })
        raise