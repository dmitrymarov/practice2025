# Система обработки запросов пользователей

## Установка и запуск

0. Убедиться, что уже установлена mediawiki - изменить переменные в .env в таком случае

1. Клонировать репозиторий:
```
git clone ...
cd practice2025
```
2. Запустить приложение:
```
docker-compose up -d
```
3. Открыть в браузере: http://localhost:5000

# 📂 Структура проекта

```
├──  .env
├──  LICENSE
├──  **app/**
│   ├──  __init__.py
│   ├──  config.py
│   ├──  **modules/**
│   │   ├──  ___init___.py
│   │   ├──  decision_graph.py
│   │   ├──  mediawiki_client.py
│   │   ├──  search_module.py
│   │   ├──  servicedesk.py
│   │   └──  ticket_storage.py
│   ├──  routes.py
│   ├──  schemas.py
│   ├──  **static/**
│   │   ├──  **css/**
│   │   │   └──  style.css
│   │   └──  **js/**
│   │       ├──  main.js
│   │       ├──  search.js
│   │       └──  servicedesk.js
│   ├──  swagger.py
│   └──  **templates/**
│       ├──  decision_tree.html
│       ├──  error.html
│       ├──  index.html
│       ├──  search.html
│       └──  servicedesk.html
├──  docker-compose.yml
├──  generate_structure.py
├──  graph_data.json
├──  mediawiki_content_creator.py
├──  mediawiki_indexer.py
├──  requirements.txt
├──  run.py
├──  test_conn.py
├──  tickets_storage.json
```