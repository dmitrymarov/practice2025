import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TicketStorage:
    """
    Класс для управления хранилищем заявок.
    Сохраняет заявки в JSON-файл для обеспечения персистентного хранения.
    """
    
    def __init__(self, file_path='tickets_storage.json'):
        """
        Инициализация хранилища
        
        Args:
            file_path (str): Путь к файлу для хранения заявок
        """
        self.file_path = file_path
        self.tickets = []
        self.next_id = 1
        self.load_tickets()
    
    def load_tickets(self):
        """Загрузка заявок из файла"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tickets = data.get('tickets', [])
                    self.next_id = data.get('next_id', 1)
                logger.info(f"Загружено {len(self.tickets)} заявок из {self.file_path}")
            except Exception as e:
                logger.error(f"Ошибка при загрузке заявок: {str(e)}")
                self.tickets = []
                self.next_id = 1
    
    def save_tickets(self):
        """Сохранение заявок в файл"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'tickets': self.tickets,
                    'next_id': self.next_id
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.tickets)} заявок в {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении заявок: {str(e)}")
            return False
    
    def get_all_tickets(self):
        """Получить все заявки"""
        return self.tickets
    
    def get_ticket(self, ticket_id):
        """Получить заявку по ID"""
        for ticket in self.tickets:
            if ticket['id'] == ticket_id:
                return ticket
        return None
    
    def create_ticket(self, subject, description, priority='normal', assigned_to=None, project_id=1):
        """Создать новую заявку"""
        ticket = {
            'id': self.next_id,
            'subject': subject,
            'description': description,
            'priority': priority,
            'status': 'new',
            'created_on': datetime.now().isoformat(),
            'project_id': project_id,
            'comments': []
        }
        
        if assigned_to:
            ticket['assigned_to'] = assigned_to
        
        self.tickets.append(ticket)
        self.next_id += 1
        self.save_tickets()
        
        return ticket
    
    def update_ticket(self, ticket_id, **kwargs):
        """Обновить заявку по ID"""
        for i, ticket in enumerate(self.tickets):
            if ticket['id'] == ticket_id:
                self.tickets[i].update(kwargs)
                self.save_tickets()
                return True
        return False
    
    def add_comment(self, ticket_id, comment):
        """Добавить комментарий к заявке"""
        for i, ticket in enumerate(self.tickets):
            if ticket['id'] == ticket_id:
                if 'comments' not in self.tickets[i]:
                    self.tickets[i]['comments'] = []
                
                self.tickets[i]['comments'].append({
                    'text': comment,
                    'created_on': datetime.now().isoformat()
                })
                self.save_tickets()
                return True
        return False
    
    def attach_solution(self, ticket_id, solution_text):
        """Прикрепить решение к заявке"""
        comment = f"Найденное решение: {solution_text}"
        return self.add_comment(ticket_id, comment)