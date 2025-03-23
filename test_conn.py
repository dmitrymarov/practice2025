import os
from dotenv import load_dotenv
import json
import logging
from opensearchpy import OpenSearch, ConnectionError, RequestError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# Configuration (from environment or defaults)
OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST', 'localhost')
OPENSEARCH_PORT = int(os.environ.get('OPENSEARCH_PORT', 9200))
OPENSEARCH_INDEX = os.environ.get('OPENSEARCH_INDEX', 'solutions')

def test_opensearch_connection():
    """Test basic connection to OpenSearch"""
    logger.info(f"Testing connection to OpenSearch at {OPENSEARCH_HOST}:{OPENSEARCH_PORT}")
    
    try:
        # Create client with extended timeout for slow connections
        client = OpenSearch(
            hosts=[{'host': OPENSEARCH_HOST, 'port': OPENSEARCH_PORT}],
            http_auth=None,
            use_ssl=False,
            verify_certs=False,
            ssl_show_warn=False,
            timeout=30,
            retry_on_timeout=True,
            max_retries=3
        )
        
        # Test connection with ping
        if client.ping():
            logger.info("✅ Successfully connected to OpenSearch")
            cluster_info = client.info()
            logger.info(f"Cluster name: {cluster_info['cluster_name']}")
            logger.info(f"OpenSearch version: {cluster_info['version']['number']}")
            return client
        else:
            logger.error("❌ Failed to connect to OpenSearch - ping failed")
            return None
    except Exception as e:
        logger.error(f"❌ Error connecting to OpenSearch: {str(e)}")
        return None

def test_index_operations(client):
    """Test index operations"""
    if not client:
        return False
    
    try:
        # Check if index exists
        index_exists = client.indices.exists(index=OPENSEARCH_INDEX)
        if index_exists:
            logger.info(f"✅ Index '{OPENSEARCH_INDEX}' exists")
            
            # Get index mapping
            mapping = client.indices.get_mapping(index=OPENSEARCH_INDEX)
            logger.info(f"Index mapping: {json.dumps(mapping, indent=2)}")
            
            # Count documents
            count = client.count(index=OPENSEARCH_INDEX)
            logger.info(f"Document count: {count['count']}")
        else:
            logger.info(f"Index '{OPENSEARCH_INDEX}' does not exist, creating it")
            
            # Create new index
            create_response = client.indices.create(
                index=OPENSEARCH_INDEX,
                body={
                    'settings': {
                        'number_of_shards': 1,
                        'number_of_replicas': 0
                    },
                    'mappings': {
                        'properties': {
                            'id': {'type': 'keyword'},
                            'title': {'type': 'text'},
                            'content': {'type': 'text'},
                            'tags': {'type': 'keyword'},
                            'source': {'type': 'keyword'}
                        }
                    }
                }
            )
            
            logger.info(f"✅ Index created: {create_response}")
            
            # Add test document
            doc = {
                'id': 'test_doc_1',
                'title': 'Test Document',
                'content': 'This is a test document to verify OpenSearch indexing and search capabilities.',
                'tags': ['test', 'opensearch', 'verification'],
                'source': 'test_script'
            }
            
            index_response = client.index(
                index=OPENSEARCH_INDEX,
                body=doc,
                id='test_doc_1',
                refresh=True
            )
            
            logger.info(f"✅ Test document indexed: {index_response['result']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing index operations: {str(e)}")
        return False

def test_search(client):
    """Test search functionality"""
    if not client:
        return False
    
    try:
        # Simple search query
        search_term = "Проблема с паролем"
        query = {
            'query': {
                'multi_match': {
                    'query': search_term,
                    'fields': ['title^2', 'content', 'tags^1.5']
                }
            }
        }
        
        logger.info(f"Executing search for '{search_term}'")
        response = client.search(
            index=OPENSEARCH_INDEX,
            body=query
        )
        
        # Log results
        hit_count = response['hits']['total']['value']
        logger.info(f"✅ Search completed. Found {hit_count} documents")
        
        if hit_count > 0:
            for hit in response['hits']['hits']:
                logger.info(f"Document: {hit['_source'].get('title')} (Score: {hit['_score']})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error testing search: {str(e)}")
        return False

def main():
    """Main test function"""
    logger.info("=== OpenSearch Test Script ===")
    
    # Test connection
    client = test_opensearch_connection()
    if not client:
        logger.error("Could not connect to OpenSearch. Please check your settings and ensure OpenSearch is running.")
        return
    
    # Test index operations
    if not test_index_operations(client):
        logger.error("Index operations failed. Check log for details.")
        return
    
    # Test search
    if not test_search(client):
        logger.error("Search operations failed. Check log for details.")
        return
    
    logger.info("✅ All tests completed successfully!")

if __name__ == "__main__":
    main()