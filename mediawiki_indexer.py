import os
import sys
import requests
from opensearchpy import OpenSearch
from dotenv import load_dotenv
import re

load_dotenv()
MEDIAWIKI_URL = os.environ.get('MEDIAWIKI_URL', 'http://localhost/mediawiki')
OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST', 'localhost')
OPENSEARCH_PORT = int(os.environ.get('OPENSEARCH_PORT', 9200))
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'solutions')

def get_mediawiki_pages():
    """Получение списка страниц из MediaWiki"""
    try:
        print("Получение списка страниц из MediaWiki...")
        response = requests.get(f"{MEDIAWIKI_URL}/api.php", params={
            'action': 'query',
            'list': 'allpages',
            'aplimit': 500,
            'format': 'json'
        })
        data = response.json()
        if 'query' in data and 'allpages' in data['query']:
            pages = data['query']['allpages']
            print(f"Найдено {len(pages)} страниц")
            return pages
        else:
            print("Не удалось получить список страниц")
            return []
    except Exception as e:
        print(f"Ошибка при получении списка страниц: {str(e)}")
        return []

def get_page_content(page_id):
    """Получение содержимого страницы по ID"""
    try:
        response = requests.get(f"{MEDIAWIKI_URL}/api.php", params={
            'action': 'parse',
            'pageid': page_id,
            'prop': 'text|categories',
            'format': 'json'
        })
        data = response.json()
        
        if 'parse' in data:
            parse_data = data['parse']
            html_content = parse_data.get('text', {}).get('*', '')
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            categories = []
            if 'categories' in parse_data:
                categories = [cat.get('*', '') for cat in parse_data['categories']]
            
            return {
                'text': text_content,
                'categories': categories
            }
        else:
            print(f"Не удалось получить содержимое для страницы {page_id}")
            return None
    except Exception as e:
        print(f"Ошибка при получении содержимого страницы {page_id}: {str(e)}")
        return None

def create_opensearch_index():
    """Создание индекса в OpenSearch"""
    try:
        client = OpenSearch(
            hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False
        )
        if client.indices.exists(index=OPENSEARCH_INDEX):
            print(f"Индекс {OPENSEARCH_INDEX} уже существует")
            return client
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "russian_english": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_stop", "english_stop", "russian_stemmer", "english_stemmer"]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "russian_english",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "russian_english"
                    },
                    "categories": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "source": {"type": "keyword"}
                }
            }
        }
        
        client.indices.create(index=OPENSEARCH_INDEX, body=settings)
        print(f"Индекс {OPENSEARCH_INDEX} успешно создан")
        return client
    except Exception as e:
        print(f"Ошибка при создании индекса: {str(e)}")
        return None

def index_page(client, page):
    """Индексация страницы в OpenSearch"""
    try:
        page_id = page['pageid']
        title = page['title']
        print(f"Индексация страницы: {title} (ID: {page_id})...")
        content_data = get_page_content(page_id)
        if not content_data:
            print(f"  Пропуск: не удалось получить содержимое")
            return False
        document = {
            'id': f"mediawiki_{page_id}",
            'title': title,
            'content': content_data['text'],
            'categories': content_data['categories'],
            'url': f"{MEDIAWIKI_URL}/index.php?curid={page_id}",
            'source': 'mediawiki'
        }
        client.index(
            index=OPENSEARCH_INDEX,
            body=document,
            id=document['id'],
            refresh=True
        )
        print(f"  Успешно проиндексировано в OpenSearch")
        return True
    except Exception as e:
        print(f"  Ошибка при индексации страницы {title}: {str(e)}")
        return False

def main():
    print("=== Индексация MediaWiki в OpenSearch ===")
    print(f"MediaWiki URL: {MEDIAWIKI_URL}")
    print(f"OpenSearch: {OPENSEARCH_HOST}:{OPENSEARCH_PORT}")
    print(f"Индекс: {OPENSEARCH_INDEX}")
    client = create_opensearch_index()
    if not client:
        print("Не удалось подключиться к OpenSearch. Проверьте настройки.")
        sys.exit(1)
    pages = get_mediawiki_pages()
    if not pages:
        print("Не найдено страниц для индексации в MediaWiki.")
        sys.exit(1)
    print(f"\nНачинаем индексацию {len(pages)} страниц...")
    success_count = 0
    for page in pages:
        if index_page(client, page):
            success_count += 1
    print(f"\nИндексация завершена.")
    print(f"Успешно проиндексировано: {success_count} из {len(pages)} страниц.")
    client.indices.refresh(index=OPENSEARCH_INDEX)
    
if __name__ == "__main__":
    main()