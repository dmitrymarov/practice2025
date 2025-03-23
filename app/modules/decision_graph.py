import json
import pydot
import networkx as nx

class DecisionGraph:
    def __init__(self):
        # Создаем направленный ациклический граф
        self.graph = nx.DiGraph()
        
    def add_node(self, node_id, content, node_type):
        """
        Добавляет узел в граф
        
        Args:
            node_id (str): Уникальный идентификатор узла
            content (str): Содержимое узла (вопрос или решение)
            node_type (str): Тип узла ('question' или 'solution')
        """
        self.graph.add_node(node_id, content=content, type=node_type)
        
    def add_edge(self, parent_id, child_id, label=None):
        """
        Добавляет связь между узлами
        
        Args:
            parent_id (str): ID родительского узла
            child_id (str): ID дочернего узла
            label (str, optional): Метка для перехода (ответ на вопрос)
        """
        self.graph.add_edge(parent_id, child_id, label=label)
        
    def get_root_node(self):
        """Возвращает корневой узел (не имеющий входящих ребер)"""
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0:
                return node
        return None
    
    def get_node_content(self, node_id):
        """Возвращает содержимое узла"""
        return self.graph.nodes[node_id]['content']
    
    def get_node_type(self, node_id):
        """Возвращает тип узла"""
        return self.graph.nodes[node_id]['type']
    
    def get_children(self, node_id):
        """Возвращает дочерние узлы"""
        children = []
        for _, child, data in self.graph.out_edges(node_id, data=True):
            children.append({
                'id': child,
                'label': data.get('label', ''),
                'content': self.graph.nodes[child]['content'],
                'type': self.graph.nodes[child]['type']
            })
        return children
    
    def is_solution(self, node_id):
        """Проверяет, является ли узел решением"""
        return self.graph.nodes[node_id]['type'] == 'solution'
    
    def save_to_file(self, filename):
        """Сохраняет граф в JSON-файл"""
        data = {
            'nodes': [],
            'edges': []
        }
        
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            data['nodes'].append({
                'id': node_id,
                'content': node_data['content'],
                'type': node_data['type']
            })
        
        for u, v, edge_data in self.graph.edges(data=True):
            data['edges'].append({
                'source': u,
                'target': v,
                'label': edge_data.get('label', '')
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filename):
        """Загружает граф из JSON-файла"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        graph = cls()
        
        for node in data['nodes']:
            graph.add_node(node['id'], node['content'], node['type'])
        
        for edge in data['edges']:
            graph.add_edge(edge['source'], edge['target'], edge['label'])
        
        return graph
    
    def visualize(self):
        """Создает DOT-представление графа для визуализации"""
        dot = pydot.Dot(graph_type='digraph')
        # Добавляем узлы
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            node_label = f"{node_id}\n{node_data['content'][:30]}..."
            
            if node_data['type'] == 'question':
                dot_node = pydot.Node(node_id, label=node_label, shape='box', style='filled', fillcolor='lightblue')
            else:
                dot_node = pydot.Node(node_id, label=node_label, shape='ellipse', style='filled', fillcolor='lightgreen')
            
            dot.add_node(dot_node)
        
        # Добавляем ребра
        for u, v, edge_data in self.graph.edges(data=True):
            edge_label = edge_data.get('label', '')
            dot_edge = pydot.Edge(u, v, label=edge_label)
            dot.add_edge(dot_edge)
        
        return dot

# Пример создания графа
def create_sample_graph():
    graph = DecisionGraph()
    
    # Добавляем узлы (вопросы и решения)
    graph.add_node('q1', 'У вас проблема с доступом к интернету или с работой приложения?', 'question')
    graph.add_node('q2', 'Проверьте подключение к Wi-Fi. Видите ли вы сеть в списке доступных?', 'question')
    graph.add_node('q3', 'Какое устройство вы используете?', 'question')
    graph.add_node('s1', 'Перезагрузите роутер и попробуйте подключиться снова.', 'solution')
    graph.add_node('s2', 'Проверьте настройки Wi-Fi на вашем устройстве. Убедитесь, что режим "В самолете" выключен.', 'solution')
    graph.add_node('q4', 'Какое приложение вызывает проблемы?', 'question')
    graph.add_node('q5', 'Какую ошибку показывает приложение?', 'question')
    graph.add_node('s3', 'Попробуйте переустановить приложение.', 'solution')
    graph.add_node('s4', 'Очистите кэш приложения и перезапустите его.', 'solution')
    
    # Добавляем связи между узлами
    graph.add_edge('q1', 'q2', 'Проблема с интернетом')
    graph.add_edge('q1', 'q4', 'Проблема с приложением')
    graph.add_edge('q2', 'q3', 'Нет')
    graph.add_edge('q2', 's1', 'Да')
    graph.add_edge('q3', 's2', 'Смартфон')
    graph.add_edge('q3', 's1', 'Компьютер')
    graph.add_edge('q4', 'q5', 'Email')
    graph.add_edge('q4', 's3', 'Браузер')
    graph.add_edge('q5', 's3', 'Ошибка авторизации')
    graph.add_edge('q5', 's4', 'Приложение зависает')
    
    return graph