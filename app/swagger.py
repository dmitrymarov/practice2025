"""
Модуль для интеграции Swagger UI с Flask-приложением.
Обеспечивает автоматическую генерацию OpenAPI спецификации и 
предоставляет веб-интерфейс для просмотра и тестирования API.
"""

from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from app.schemas import (
    NodeSchema, SearchQuerySchema, SearchResultSchema, SearchResponseSchema,
    TicketCreateSchema, CommentCreateSchema, SolutionAttachSchema, StatusResponseSchema
)
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

# Регистрация маршрутов API в спецификации
def register_api_routes(app):
    """Регистрирует все маршруты API в спецификации OpenAPI"""
    # Сначала регистрируем схемы
    register_schemas()
    
    # Маршрут для получения узла графа решений
    spec.path(
        path="/api/node/{node_id}",
        operations={
            "get": {
                "tags": ["decision-tree"],
                "summary": "Получить данные узла графа решений",
                "description": "Возвращает информацию об узле графа решений по его ID. "
                              "Для получения корневого узла используйте 'root' в качестве node_id.",
                "parameters": [
                    {
                        "name": "node_id",
                        "in": "path",
                        "required": True,
                        "description": "ID узла графа (или 'root' для корневого узла)",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Успешный ответ",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Node"}
                            }
                        }
                    },
                    "404": {
                        "description": "Узел не найден",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                },
                                "example": {"error": "Node not found"}
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )
    
    # Маршрут для поиска решений
    spec.path(
        path="/api/search",
        operations={
            "post": {
                "tags": ["search"],
                "summary": "Поиск решений по запросу",
                "description": "Выполняет поиск решений на основе текстового запроса. "
                              "Поиск осуществляется в OpenSearch и других источниках, в зависимости от настроек.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SearchQuery"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результаты поиска",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SearchResponse"}
                            }
                        }
                    },
                    "500": {
                        "description": "Ошибка сервера",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )
    
    # Маршрут для создания заявки
    spec.path(
        path="/api/tickets",
        operations={
            "post": {
                "tags": ["servicedesk"],
                "summary": "Создать новую заявку",
                "description": "Создает новую заявку в системе Service Desk на основе предоставленных данных.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TicketCreate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Заявка успешно создана",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "subject": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "status": {"type": "string"},
                                        "created_on": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        }
                    },
                    "500": {
                        "description": "Ошибка создания заявки",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )
    
    # Маршрут для получения заявки по ID
    spec.path(
        path="/api/tickets/{ticket_id}",
        operations={
            "get": {
                "tags": ["servicedesk"],
                "summary": "Получить информацию о заявке",
                "description": "Возвращает подробную информацию о заявке по её ID.",
                "parameters": [
                    {
                        "name": "ticket_id",
                        "in": "path",
                        "required": True,
                        "description": "ID заявки",
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Информация о заявке",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "subject": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "status": {"type": "string"},
                                        "created_on": {"type": "string", "format": "date-time"},
                                        "comments": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "text": {"type": "string"},
                                                    "created_on": {"type": "string", "format": "date-time"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "404": {
                        "description": "Заявка не найдена",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                },
                                "example": {"error": "Ticket not found"}
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )
    
    # Маршрут для добавления комментария к заявке
    spec.path(
        path="/api/tickets/{ticket_id}/comment",
        operations={
            "post": {
                "tags": ["servicedesk"],
                "summary": "Добавить комментарий к заявке",
                "description": "Добавляет новый комментарий к существующей заявке.",
                "parameters": [
                    {
                        "name": "ticket_id",
                        "in": "path",
                        "required": True,
                        "description": "ID заявки",
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CommentCreate"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Комментарий успешно добавлен",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StatusResponse"}
                            }
                        }
                    },
                    "500": {
                        "description": "Ошибка при добавлении комментария",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                },
                                "example": {"error": "Failed to add comment"}
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )
    
    # Маршрут для прикрепления решения к заявке
    spec.path(
        path="/api/tickets/{ticket_id}/solution",
        operations={
            "post": {
                "tags": ["servicedesk"],
                "summary": "Прикрепить решение к заявке",
                "description": "Прикрепляет найденное решение к существующей заявке.",
                "parameters": [
                    {
                        "name": "ticket_id",
                        "in": "path",
                        "required": True,
                        "description": "ID заявки",
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SolutionAttach"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Решение успешно прикреплено",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/StatusResponse"}
                            }
                        }
                    },
                    "500": {
                        "description": "Ошибка при прикреплении решения",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "error": {"type": "string"}
                                    }
                                },
                                "example": {"error": "Failed to attach solution"}
                            }
                        }
                    }
                }
            }
        },
        path_parameters={}
    )