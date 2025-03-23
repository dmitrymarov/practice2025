from flask import Blueprint, render_template, request, jsonify, current_app
from app import decision_graph, search_module, service_desk

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@bp.route('/decision-tree')
def decision_tree():
    """Страница диалогового модуля"""
    return render_template('decision_tree.html')

@bp.route('/search')
def search():
    """Страница поиска"""
    return render_template('search.html')

@bp.route('/servicedesk')
def servicedesk():
    """Страница работы с заявками"""
    return render_template('servicedesk.html')

# API для диалогового модуля
@bp.route('/api/node/<node_id>', methods=['GET'])
def get_node(node_id):
    """Получить данные узла"""
    if node_id == 'root':
        node_id = decision_graph.get_root_node()
    
    if not node_id or node_id not in decision_graph.graph.nodes():
        return jsonify({'error': 'Node not found'}), 404
    
    node_content = decision_graph.get_node_content(node_id)
    node_type = decision_graph.get_node_type(node_id)
    children = decision_graph.get_children(node_id)
    
    return jsonify({
        'id': node_id,
        'content': node_content,
        'type': node_type,
        'children': children
    })

# API для модуля поиска
@bp.route('/api/search', methods=['POST'])
def search_api():
    """Поиск решений через оригинальный модуль поиска"""
    try:
        # Получаем данные запроса
        query = request.json.get('query', '')
        # Выполняем поиск через модуль поиска, включая поиск в MediaWiki
        results = search_module.search(
            query_text=query,
            mediawiki_url=current_app.config.get('MEDIAWIKI_URL')
        )
        # Отправляем результаты поиска
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e), 'results': []}), 500

# API для индексации MediaWiki контента в OpenSearch
@bp.route('/api/index-mediawiki', methods=['POST'])
def index_mediawiki():
    """Индексировать статью из MediaWiki в OpenSearch"""
    if not current_app.config['USE_MEDIAWIKI'] or current_app.config['USE_MOCK_SERVICES']:
        return jsonify({'error': 'MediaWiki integration is not enabled'}), 400
    
    page_id = request.json.get('page_id')
    if not page_id:
        return jsonify({'error': 'Page ID is required'}), 400
    
    success = search_module.index_mediawiki_content(page_id)
    if success:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'error': 'Failed to index MediaWiki content'}), 500

# API для работы с Service Desk
@bp.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Создать заявку"""
    data = request.json
    ticket = service_desk.create_ticket(
        subject=data.get('subject', ''),
        description=data.get('description', ''),
        priority=data.get('priority', 'normal'),
        assigned_to=data.get('assigned_to'),
        project_id=data.get('project_id', 1)
    )
    return jsonify(ticket)

@bp.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Получить данные заявки"""
    ticket = service_desk.get_ticket(ticket_id)
    if ticket:
        return jsonify(ticket)
    return jsonify({'error': 'Ticket not found'}), 404

@bp.route('/api/tickets/<int:ticket_id>/comment', methods=['POST'])
def add_comment(ticket_id):
    """Добавить комментарий к заявке"""
    comment = request.json.get('comment', '')
    success = service_desk.add_comment(ticket_id, comment)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to add comment'}), 500

@bp.route('/api/tickets/<int:ticket_id>/solution', methods=['POST'])
def attach_solution(ticket_id):
    """Прикрепить решение к заявке"""
    solution = request.json.get('solution', '')
    source = request.json.get('source', 'unknown')
    
    # Добавляем информацию об источнике решения
    solution_text = f"{solution}\n\nИсточник: {get_source_label(source)}"
    
    success = service_desk.attach_solution(ticket_id, solution_text)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to attach solution'}), 500

# Вспомогательная функция для получения читаемого названия источника
def get_source_label(source):
    source_labels = {
        'opensearch': 'OpenSearch',
        'mediawiki': 'MediaWiki',
        'mock': 'База знаний (демо)'
    }
    return source_labels.get(source, 'Неизвестный источник')