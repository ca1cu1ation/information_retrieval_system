# Configuration file for Elasticsearch indices

# News Index Configuration
NEWS_INDEX_SETTINGS = {
    "index": {
        "number_of_replicas": 1,
        "number_of_shards": 2
    },
    "analysis": {
        "filter": {
            "autocomplete_filter": {
                "type": "edge_ngram",
                "min_gram": 2,
                "max_gram": 20
            }
        },
        "analyzer": {
            "autocomplete": {
                "type": "custom",
                "tokenizer": "ik_smart",
                "filter": [
                    "lowercase",
                    "autocomplete_filter"
                ]
            },
            "ik_max_word_analyzer": {
                "type": "custom",
                "tokenizer": "ik_max_word",
                "filter": ["lowercase"]
            }
        }
    }
}

NEWS_INDEX_MAPPINGS = {
    "properties": {
        "ctime": {"type": "date", "format": "yyyy-MM-dd HH:mm"},
        "url": {"type": "keyword"},
        "wapurl": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "ik_max_word",
            "fields": {
                "autocomplete": {
                    "type": "text",
                    "analyzer": "autocomplete"
                }
            }
        },
        "media_name": {"type": "keyword"},
        "keywords": {"type": "text", "analyzer": "ik_max_word"},
        "content": {"type": "text", "analyzer": "ik_max_word"}
    }
}

# Documents Index Configuration
DOCUMENTS_INDEX_SETTINGS = {
    "index": {
        "number_of_replicas": 1,
        "number_of_shards": 1
    },
    "analysis": {
        "analyzer": {
            "ik_max_word_analyzer": {
                "type": "custom",
                "tokenizer": "ik_max_word",
                "filter": ["lowercase"]
            }
        }
    }
}

DOCUMENTS_INDEX_MAPPINGS = {
    "properties": {
        "file_name": {"type": "keyword"},
        "content": {"type": "text", "analyzer": "ik_max_word"},
        "file_path": {"type": "keyword"},
        "download_url": {"type": "keyword"},
        "timestamp": {"type": "date"},
        "file_type": {"type": "keyword"},
        "file_size": {"type": "long"}
    }
}