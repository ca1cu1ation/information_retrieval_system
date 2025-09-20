import os
from typing import Dict, Any

class Config:
    """Configuration class for the Information Retrieval System"""
    
    # Elasticsearch Configuration
    ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
    ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))
    ELASTICSEARCH_USERNAME = os.getenv('ELASTICSEARCH_USERNAME', '')
    ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD', '')
    
    # Elasticsearch Index Names
    NEWS_INDEX = 'news_index'
    DOCUMENTS_INDEX = 'documents_index'
    
    # MySQL Database Configuration
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'Qwe248931'),
        'database': os.getenv('MYSQL_DATABASE', 'web_search'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'pool_name': 'mypool',
        'pool_size': 5,
        'buffered': True
    }
    
    # Flask Server Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 3000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # File Storage Configuration
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', './documents')
    SNAPSHOT_FOLDER = os.getenv('SNAPSHOT_FOLDER', './snapshots')
    
    # Search Configuration
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 10))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'search.log')
    
    @classmethod
    def get_elasticsearch_config(cls) -> Dict[str, Any]:
        """Get Elasticsearch connection configuration"""
        config = {
            'hosts': [f"http://{cls.ELASTICSEARCH_HOST}:{cls.ELASTICSEARCH_PORT}"],
            'headers': {"Accept": "application/json"},
            'verify_certs': False,
            'meta_header': False,
        }
        
        if cls.ELASTICSEARCH_USERNAME and cls.ELASTICSEARCH_PASSWORD:
            config['basic_auth'] = (cls.ELASTICSEARCH_USERNAME, cls.ELASTICSEARCH_PASSWORD)
            
        return config