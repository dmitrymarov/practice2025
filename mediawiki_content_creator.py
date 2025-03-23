#!/usr/bin/env python3
"""
Скрипт для создания и редактирования страниц в MediaWiki
с содержанием для демонстрации поиска решений.
Включает расширенную обработку ошибок и альтернативные методы.
"""

import os
import sys
import argparse
import requests
import json
from dotenv import load_dotenv
from time import sleep
import html

# Загрузка переменных окружения
load_dotenv()

# Настройки из переменных окружения
MEDIAWIKI_URL = os.environ.get('MEDIAWIKI_URL', 'http://localhost/mediawiki')
MEDIAWIKI_USERNAME = os.environ.get('MEDIAWIKI_USERNAME')
MEDIAWIKI_PASSWORD = os.environ.get('MEDIAWIKI_PASSWORD')

class MediaWikiContentCreator:
    def __init__(self, mediawiki_url, username, password):
        self.mediawiki_url = mediawiki_url
        self.mediawiki_api = f"{mediawiki_url}/api.php"
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ContentCreatorScript/1.0 (custom script for educational purpose)'
        })
        
        # Выполняем вход
        if not self.login():
            print("Не удалось войти в MediaWiki. Проверьте учетные данные.")
            sys.exit(1)
    
    def login(self):
        """Авторизация в MediaWiki"""
        # Получение токена для входа
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        
        try:
            response = self.session.get(self.mediawiki_api, params=params)
            data = response.json()
            
            if 'query' in data and 'tokens' in data['query'] and 'logintoken' in data['query']['tokens']:
                login_token = data['query']['tokens']['logintoken']
                
                # Выполнение входа
                params = {
                    'action': 'login',
                    'lgname': self.username,
                    'lgpassword': self.password,
                    'lgtoken': login_token,
                    'format': 'json'
                }
                
                response = self.session.post(self.mediawiki_api, data=params)
                login_result = response.json()
                
                if login_result.get('login', {}).get('result') == 'Success':
                    print(f"Успешный вход в MediaWiki как {self.username}")
                    return True
                else:
                    print(f"Ошибка авторизации в MediaWiki: {login_result}")
                    return False
            else:
                print("Не удалось получить токен для входа в MediaWiki")
                return False
        except Exception as e:
            print(f"Ошибка при авторизации: {str(e)}")
            return False
    
    def get_csrf_token(self):
        """Получение CSRF-токена для редактирования страниц"""
        params = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        
        response = self.session.get(self.mediawiki_api, params=params)
        data = response.json()
        
        if 'query' in data and 'tokens' in data['query'] and 'csrftoken' in data['query']['tokens']:
            return data['query']['tokens']['csrftoken']
        else:
            print("Не удалось получить CSRF-токен")
            return None
    
    def create_page(self, title, content, summary="Автоматическое создание страницы"):
        """Создание или редактирование страницы"""
        token = self.get_csrf_token()
        if not token:
            return False
        
        # Попробуем сначала метод API edit
        success = self._create_via_api(title, content, summary, token)
        
        # Если API не сработал, попробуем альтернативные методы
        if not success:
            print(f"Пробуем альтернативный метод для '{title}'...")
            success = self._create_via_web_form(title, content, summary)
            
        return success
    
    def _create_via_api(self, title, content, summary, token):
        """Создание страницы через API"""
        try:
            # Очистка контента от потенциально проблемных элементов
            # content = html.escape(content)
            
            params = {
                'action': 'edit',
                'title': title,
                'text': content,
                'summary': summary,
                'token': token,
                'format': 'json',
                # Дополнительные параметры, которые могут помочь
                'contentmodel': 'wikitext',
                'utf8': 1,
                'bot': 1  # Пометка как действие бота (если аккаунт имеет права бота)
            }
            
            response = self.session.post(self.mediawiki_api, data=params)
            data = response.json()
            
            if 'edit' in data and data['edit']['result'] == 'Success':
                print(f"Страница '{title}' успешно создана/обновлена")
                return True
            else:
                print(f"Ошибка при создании страницы '{title}' через API: {data}")
                return False
        except Exception as e:
            print(f"Исключение при создании страницы '{title}' через API: {str(e)}")
            return False
    
    def _create_via_web_form(self, title, content, summary):
        """
        Альтернативный метод создания страницы через форму редактирования.
        Это может сработать, если API блокируется расширением.
        """
        try:
            # Получаем токен из формы редактирования
            edit_url = f"{self.mediawiki_url}/index.php?title={title}&action=edit"
            response = self.session.get(edit_url)
            
            # Находим токен в HTML (это упрощенная версия, может потребоваться доработка)
            import re
            edit_token_match = re.search(r'wpEditToken"\s+value="([^"]+)"', response.text)
            if edit_token_match:
                edit_token = edit_token_match.group(1)
                
                # Отправляем форму
                edit_data = {
                    'wpTextbox1': content,
                    'wpSummary': summary,
                    'wpEditToken': edit_token,
                    'wpSave': 'Сохранить страницу'
                }
                
                submit_url = f"{self.mediawiki_url}/index.php?title={title}&action=submit"
                response = self.session.post(submit_url, data=edit_data)
                
                # Проверяем успешность (очень простая проверка)
                if response.status_code == 200 and 'class="errorbox"' not in response.text:
                    print(f"Страница '{title}' успешно создана через веб-форму")
                    return True
                else:
                    print(f"Ошибка при создании страницы '{title}' через веб-форму")
                    return False
            else:
                print(f"Не удалось найти токен редактирования для '{title}'")
                return False
        except Exception as e:
            print(f"Исключение при создании страницы '{title}' через веб-форму: {str(e)}")
            return False
    
    def create_page_simplified(self, title, content):
        """
        Упрощенный метод создания страницы.
        Создает минимальное содержимое, которое с большей вероятностью будет принято.
        """
        # Упрощаем контент до минимума
        simplified_content = f"""== {title} ==

{content}

"""
        return self.create_page(title, simplified_content, "Создание базовой страницы")
    
    def create_demo_content(self):
        """Создание демонстрационного контента для поиска решений"""
        # Создание категорий
        categories = [
            "Категория:Сетевые проблемы",
            "Категория:Программное обеспечение",
            "Категория:Аппаратные проблемы",
            "Категория:Учетные записи",
            "Категория:Часто задаваемые вопросы"
        ]
        
        for category in categories:
            category_description = f"Категория для организации статей по теме '{category.replace('Категория:', '')}'."
            if self.create_page(category, category_description, "Создание категории"):
                print(f"Создана категория: {category}")
            sleep(1)
        
        # Создание простого контента для демонстрации
        # Используем упрощенный формат, чтобы избежать проблем с разметкой
        simple_pages = [
            {
                "title": "Wi-Fi проблемы",
                "content": """
Проблемы с Wi-Fi часто включают:

1. Не видно сеть Wi-Fi
2. Не удается подключиться к сети
3. Частые обрывы соединения
4. Медленная скорость соединения

Решения:
* Перезагрузите роутер
* Проверьте настройки Wi-Fi на устройстве
* Убедитесь, что режим "В самолете" выключен
* Переместитесь ближе к роутеру

[[Категория:Сетевые проблемы]]
"""
            },
            {
                "title": "Проблемы с браузером",
                "content": """
Распространенные проблемы с браузером:

1. Браузер зависает
2. Страницы не загружаются
3. Медленная работа
4. Нежелательная реклама

Решения:
* Очистите кэш и историю
* Отключите ненужные расширения
* Обновите браузер до последней версии
* Проверьте подключение к интернету

[[Категория:Программное обеспечение]]
"""
            },
            {
                "title": "Перегрев компьютера",
                "content": """
Симптомы перегрева компьютера:

1. Спонтанные выключения
2. Снижение производительности
3. Повышенный шум вентиляторов

Решения:
* Очистите компьютер от пыли
* Проверьте работу вентиляторов
* Замените термопасту
* Используйте охлаждающую подставку для ноутбука

[[Категория:Аппаратные проблемы]]
"""
            },
            {
                "title": "Забытый пароль",
                "content": """
Что делать, если забыли пароль:

1. Используйте опцию "Забыли пароль" на странице входа
2. Проверьте привязанную электронную почту
3. Ответьте на контрольные вопросы
4. Свяжитесь с администратором системы

Профилактика:
* Используйте менеджер паролей
* Настройте двухфакторную аутентификацию
* Создайте уникальные, сложные пароли

[[Категория:Учетные записи]]
[[Категория:Часто задаваемые вопросы]]
"""
            },
            {
                "title": "Компьютерная безопасность",
                "content": """
Основы компьютерной безопасности:

1. Установите антивирус и регулярно обновляйте его
2. Не открывайте подозрительные вложения в письмах
3. Используйте сложные пароли
4. Регулярно обновляйте программное обеспечение
5. Будьте осторожны с публичными Wi-Fi сетями

Дополнительные рекомендации:
* Шифруйте важные данные
* Делайте регулярные резервные копии
* Используйте VPN при подключении к общественным сетям

[[Категория:Часто задаваемые вопросы]]
"""
            },
        ]
        
        # Создаем простые страницы
        for page in simple_pages:
            if self.create_page_simplified(page["title"], page["content"]):
                print(f"Страница '{page['title']}' успешно создана")
            else:
                print(f"Не удалось создать страницу '{page['title']}'")
            sleep(1)
        
        print("Создание базового демонстрационного контента завершено!")

def main():
    if not MEDIAWIKI_URL or not MEDIAWIKI_USERNAME or not MEDIAWIKI_PASSWORD:
        print("Ошибка: Необходимо указать URL MediaWiki и учетные данные в .env файле")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description='Создание контента в MediaWiki')
    parser.add_argument('--debug', action='store_true', help='Режим отладки с подробными логами')
    args = parser.parse_args()
    
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
    creator = MediaWikiContentCreator(MEDIAWIKI_URL, MEDIAWIKI_USERNAME, MEDIAWIKI_PASSWORD)
    creator.create_demo_content()

if __name__ == "__main__":
    main()