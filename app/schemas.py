from marshmallow import Schema, fields

class NodeSchema(Schema):
    """Схема для узла графа решений"""
    id = fields.Str(required=True, description="Идентификатор узла")
    content = fields.Str(required=True, description="Содержимое узла (вопрос или решение)")
    type = fields.Str(required=True, description="Тип узла (question или solution)")
    children = fields.List(fields.Dict(), description="Список дочерних узлов")

class NodeChildSchema(Schema):
    """Схема для дочернего узла"""
    id = fields.Str(required=True, description="Идентификатор узла")
    label = fields.Str(description="Метка перехода к узлу")
    content = fields.Str(description="Содержимое узла")
    type = fields.Str(description="Тип узла")

class SearchQuerySchema(Schema):
    """Схема для поискового запроса"""
    query = fields.Str(required=True, description="Текст поискового запроса")

class SearchResultSchema(Schema):
    """Схема для результата поиска"""
    id = fields.Str(required=True, description="Идентификатор результата")
    title = fields.Str(required=True, description="Заголовок")
    content = fields.Str(required=True, description="Содержимое")
    score = fields.Float(required=True, description="Релевантность")
    source = fields.Str(description="Источник данных (opensearch, mediawiki, mock)")
    url = fields.Str(description="URL для перехода к источнику")
    highlight = fields.Str(description="Подсвеченный фрагмент текста")

class SearchResponseSchema(Schema):
    """Схема для ответа на поисковый запрос"""
    results = fields.List(fields.Nested(SearchResultSchema), description="Список результатов поиска")

class TicketCreateSchema(Schema):
    """Схема для создания заявки"""
    subject = fields.Str(required=True, description="Тема заявки")
    description = fields.Str(required=True, description="Описание проблемы")
    priority = fields.Str(default="normal", description="Приоритет (low, normal, high, urgent)")
    assigned_to = fields.Int(description="ID исполнителя")
    project_id = fields.Int(default=1, description="ID проекта")

class CommentCreateSchema(Schema):
    """Схема для создания комментария"""
    comment = fields.Str(required=True, description="Текст комментария")

class SolutionAttachSchema(Schema):
    """Схема для прикрепления решения"""
    solution = fields.Str(required=True, description="Текст решения")
    source = fields.Str(default="unknown", description="Источник решения")

class StatusResponseSchema(Schema):
    """Схема для ответа со статусом операции"""
    status = fields.Str(required=True, description="Статус операции")