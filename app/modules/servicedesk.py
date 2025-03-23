import requests

class ServiceDeskModule:
    def __init__(self, api_url=None, api_key=None, use_mock=True):
        self.use_mock = use_mock
        self.tickets = []
        self.next_ticket_id = 1
        
        if not use_mock:
            if not api_url or not api_key:
                raise ValueError("API URL and API key are required for real ServiceDesk integration")
                
            self.api_url = api_url
            self.headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": api_key
            }
    
    def create_ticket(self, subject, description, priority='normal', assigned_to=None, project_id=1):
        """
        Создать новую заявку в Service Desk
        
        Args:
            subject (str): Тема заявки
            description (str): Описание проблемы
            priority (str): Приоритет ('low', 'normal', 'high', 'urgent')
            assigned_to (int, optional): ID исполнителя
            project_id (int): ID проекта
            
        Returns:
            dict: Данные созданной заявки
        """
        if self.use_mock:
            # Имитация создания заявки
            ticket = {
                'id': self.next_ticket_id,
                'subject': subject,
                'description': description,
                'priority': priority,
                'status': 'new',
                'created_on': '2025-03-22T10:00:00Z',
                'project_id': project_id,
                'comments': []
            }
            
            if assigned_to:
                ticket['assigned_to'] = assigned_to
                
            self.tickets.append(ticket)
            self.next_ticket_id += 1
            
            return ticket
        else:
            # Реальное API Redmine
            issue_data = {
                'issue': {
                    'subject': subject,
                    'description': description,
                    'project_id': project_id,
                    'priority_id': self._get_priority_id(priority)
                }
            }
            
            if assigned_to:
                issue_data['issue']['assigned_to_id'] = assigned_to
                
            response = requests.post(
                f"{self.api_url}/issues.json",
                headers=self.headers,
                json=issue_data
            )
            
            if response.status_code in (200, 201):
                return response.json()['issue']
            else:
                raise Exception(f"Failed to create ticket: {response.text}")
    
    def get_ticket(self, ticket_id):
        """
        Получить заявку по ID
        
        Args:
            ticket_id (int): ID заявки
            
        Returns:
            dict: Данные заявки
        """
        if self.use_mock:
            for ticket in self.tickets:
                if ticket['id'] == ticket_id:
                    return ticket
            return None
        else:
            response = requests.get(
                f"{self.api_url}/issues/{ticket_id}.json",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()['issue']
            else:
                return None
    
    def update_ticket(self, ticket_id, **kwargs):
        """
        Обновить заявку
        
        Args:
            ticket_id (int): ID заявки
            **kwargs: Поля для обновления (subject, description, status, etc.)
            
        Returns:
            bool: Успешность операции
        """
        if self.use_mock:
            for i, ticket in enumerate(self.tickets):
                if ticket['id'] == ticket_id:
                    self.tickets[i].update(kwargs)
                    return True
            return False
        else:
            issue_data = {
                'issue': kwargs
            }
            
            response = requests.put(
                f"{self.api_url}/issues/{ticket_id}.json",
                headers=self.headers,
                json=issue_data
            )
            
            return response.status_code == 200
    
    def add_comment(self, ticket_id, comment):
        """
        Добавить комментарий к заявке
        
        Args:
            ticket_id (int): ID заявки
            comment (str): Текст комментария
            
        Returns:
            bool: Успешность операции
        """
        if self.use_mock:
            for i, ticket in enumerate(self.tickets):
                if ticket['id'] == ticket_id:
                    if 'comments' not in self.tickets[i]:
                        self.tickets[i]['comments'] = []
                    
                    self.tickets[i]['comments'].append({
                        'text': comment,
                        'created_on': '2025-03-22T10:30:00Z'
                    })
                    return True
            return False
        else:
            issue_data = {
                'issue': {
                    'notes': comment
                }
            }
            
            response = requests.put(
                f"{self.api_url}/issues/{ticket_id}.json",
                headers=self.headers,
                json=issue_data
            )
            
            return response.status_code == 200
    
    def attach_solution(self, ticket_id, solution_text):
        """
        Прикрепить решение к заявке
        
        Args:
            ticket_id (int): ID заявки
            solution_text (str): Текст решения
            
        Returns:
            bool: Успешность операции
        """
        return self.add_comment(ticket_id, f"Найденное решение: {solution_text}")
    
    def _get_priority_id(self, priority_name):
        """Преобразует текстовый приоритет в ID для Redmine"""
        priorities = {
            'low': 1,
            'normal': 2,
            'high': 3,
            'urgent': 4
        }
        return priorities.get(priority_name.lower(), 2)  # По умолчанию 'normal'