from elasticsearch import Elasticsearch
import mysql.connector

# 连接到Elasticsearch
USERNAME = ""
PASSWORD = ""
es = Elasticsearch(
    ["http://localhost:9200"],
    basic_auth=(USERNAME, PASSWORD),
    headers={"Accept": "application/json"},
    verify_certs=False,
    meta_header=False,
)

# 设置Elasticsearch索引的映射和配置
settings = {
    "index": {
        "number_of_replicas": 2,
        "number_of_shards": 3
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
            "autocomplete": {  # 自动补全分析器
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

mappings = {
    "properties": {
        "ctime": {"type": "date", "format": "YYYY-MM-DD HH:mm"},
        "url": {"type": "keyword"},
        "wapurl": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "ik_max_word",
            "fields": {
                "autocomplete": {  # 为标题添加自动补全字段
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


# 创建Elasticsearch索引（如果不存在）
index_name = "news_index"
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
es.indices.create(
    index=index_name,
    settings =settings,
    mappings = mappings
)

# 连接到Mysql数据库
conn=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Qwe248931",
    database="web_search"
)
cursor = conn.cursor(dictionary=True)  # 使用字典模式获取结果

# 执行查询
cursor.execute("SELECT * FROM nankai_news")

# 遍历 MySQL 结果集
for row in cursor:
    # 生成文档ID
    doc_id = str(row['id'])

    # 处理日期格式转换
    row["ctime"] = row["ctime"].strftime("%Y-%m-%d %H:%M")

    # 创建文档副本并移除 id
    doc = dict(row)
    del doc['id']  # 移除 MySQL 自增ID

    # 索引文档到 Elasticsearch（保持与原来相同的逻辑）
    es.index(index=index_name, id=doc_id,document=doc)

    content = doc.get("content", "")

# 关闭连接
cursor.close()
conn.close()
