from elasticsearch import Elasticsearch

USERNAME = ""
PASSWORD = ""
es = Elasticsearch(
    ["http://localhost:9200"],
    basic_auth=(USERNAME, PASSWORD),
    headers={"Accept": "application/json"},
    verify_certs=False,
    meta_header=False,
)
index_name = "documents_index"

def search_documents(query):
    try:
        result = es.search(
            index=index_name,
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["content", "file_name"],
                    "type": "best_fields"
                }
             },
            highlight={
                "fields": {
                    "content": {
                        "pre_tags": ["<em>"],
                        "post_tags": ["</em>"]
                    }
                }
            },
            size = 10
        )
        hits = result.get('hits', {}).get('hits', [])
        search_results = []
        for hit in hits:
            source = hit['_source']
            search_results.append({
                "file_name": source['file_name'],
                "url": source['download_url'],
                "content": source['content'][:200] + "...",
                "highlight": hit.get('highlight', {}).get('content', [])
            })
        return search_results
    except Exception as e:
        print(f"搜索失败: {e}")
        return []
