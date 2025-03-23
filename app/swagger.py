from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from app.schemas import (
    NodeSchema, SearchQuerySchema, SearchResultSchema, SearchResponseSchema,
    TicketCreateSchema, CommentCreateSchema, SolutionAttachSchema, StatusResponseSchema
)
import logging

logger = logging.getLogger(__name__)

# Создаем спецификацию API
spec = APISpec(
    title="Система обработки запросов - API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="API для системы обработки запросов пользователей. "
                  "Предоставляет доступ к модулям поиска решений, графа решений и управления заявками.",
        contact=dict(email="admin@example.com")
    ),
    servers=[
        {"url": "/", "description": "Локальный сервер"}
    ],
    tags=[
        {"name": "decision-tree", "description": "Работа с диалоговым модулем (графом решений)"},
        {"name": "search", "description": "Поиск решений по запросу"},
        {"name": "servicedesk", "description": "Управление заявками в системе Service Desk"}
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Создаем Blueprint для Swagger UI
SWAGGER_URL = '/api/docs'  # URL для доступа к UI
API_URL = '/api/swagger.json'  # URL для JSON-файла спецификации API

# Настройки интерфейса Swagger UI
swagger_ui_config = {
    'app_name': "Система обработки запросов - API",
    'dom_id': '#swagger-ui',
    'layout': 'BaseLayout',
    'deepLinking': True,
    'supportedSubmitMethods': ['get', 'post', 'put', 'delete'],
    'validatorUrl': None,
    'docExpansion': 'list',  # 'none', 'list' или 'full'
    'defaultModelsExpandDepth': 1,
}

swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config=swagger_ui_config
)

# Blueprint для API спецификации
api_spec_blueprint = Blueprint('api_spec', __name__)

@api_spec_blueprint.route('/api/swagger.json')
def create_swagger_spec():
    """Возвращает спецификацию API в формате JSON"""
    return jsonify(spec.to_dict())

# Регистрация схем в спецификации
def register_schemas():
    """Регистрирует все схемы Marshmallow в спецификации API"""
    spec.components.schema("Node", schema=NodeSchema)
    spec.components.schema("SearchQuery", schema=SearchQuerySchema)
    spec.components.schema("SearchResult", schema=SearchResultSchema)
    spec.components.schema("SearchResponse", schema=SearchResponseSchema)
    spec.components.schema("TicketCreate", schema=TicketCreateSchema)
    spec.components.schema("CommentCreate", schema=CommentCreateSchema)
    spec.components.schema("SolutionAttach", schema=SolutionAttachSchema)
    spec.components.schema("StatusResponse", schema=StatusResponseSchema)

def register_api_routes(app):
    """Регистрирует все маршруты API в спецификации OpenAPI"""
    # Сначала регистрируем схемы
    register_schemas()
    
    try:
        # Получаем все зарегистрированные URL-правила
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('main.') and '/api/' in rule.rule:
                logger.info(f"Зарегистрировано API правило: {rule.rule} ({rule.endpoint})")
            
        # Упрощенная версия - добавляем только документацию и конечные точки
        spec_paths = {
            "/api/node/{node_id}": {
                "get": {
                    "tags": ["decision-tree"],
                    "summary": "Получить данные узла графа решений",
                    "parameters": [
                        {
                            "name": "node_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Успешный ответ",
                            "content": {"application/json": {}}
                        }
                    }
                }
            },
            "/api/search": {
                "post": {
                    "tags": ["search"],
                    "summary": "Поиск решений по запросу",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {}}
                    },
                    "responses": {
                        "200": {
                            "description": "Результаты поиска",
                            "content": {"application/json": {}}
                        }
                    }
                }
            },
            "/api/tickets": {
                "post": {
                    "tags": ["servicedesk"],
                    "summary": "Создать новую заявку",
                    "responses": {
                        "200": {"description": "Заявка создана"}
                    }
                }
            },
            "/api/tickets/{ticket_id}": {
                "get": {
                    "tags": ["servicedesk"],
                    "summary": "Получить информацию о заявке",
                    "parameters": [
                        {
                            "name": "ticket_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Информация о заявке"}
                    }
                }
            },
            "/api/tickets/{ticket_id}/comment": {
                "post": {
                    "tags": ["servicedesk"],
                    "summary": "Добавить комментарий к заявке",
                    "parameters": [
                        {
                            "name": "ticket_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Комментарий добавлен"}
                    }
                }
            },
            "/api/tickets/{ticket_id}/solution": {
                "post": {
                    "tags": ["servicedesk"],
                    "summary": "Прикрепить решение к заявке",
                    "parameters": [
                        {
                            "name": "ticket_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {"description": "Решение прикреплено"}
                    }
                }
            }
        }
        
        # Добавляем пути в спецификацию напрямую
        for path, operations in spec_paths.items():
            spec.path(path=path, operations=operations)
        
        logger.info("API маршруты успешно зарегистрированы в спецификации")
    except Exception as e:
        logger.error(f"Ошибка при регистрации API маршрутов: {str(e)}")
        # Не позволяем ошибке остановить приложение
        print(f"Предупреждение: Не удалось полностью инициализировать документацию API: {str(e)}")
        print("Swagger UI может работать некорректно. Проверьте логи для деталей.")