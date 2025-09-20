import os
import webbrowser
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from functools import wraps
from document_search import search_documents
import logging
from mysql.connector import pooling
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app)
# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Qwe248931',
    'database': 'web_search',
    'pool_name': 'mypool',
    'pool_size': 5,
    'buffered': True
}

# 连接到Elasticsearch
USERNAME = ""
PASSWORD = ""
ES_INDEX = "news_index"
es = Elasticsearch(
    ["http://localhost:9200"],
    basic_auth=(USERNAME, PASSWORD),
    headers={"Accept": "application/json"},
    verify_certs=False,
    meta_header=False,
)

# 创建连接池
try:
    connection_pool = pooling.MySQLConnectionPool(**db_config)
    print("成功创建数据库连接池")
except mysql.connector.Error as err:
    print(f"数据库连接错误: {err}")


def get_db_connection():
    return connection_pool.get_connection()


# 密码验证函数
def verify_password(plain_password, hashed_password):
    return plain_password.encode('utf-8') == hashed_password.encode('utf-8')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('username')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, password FROM user WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "用户不存在"}), 401

        if not verify_password(password, user['password']):
            return jsonify({"success": False, "message": "密码错误"}), 401

        # 登录成功，返回用户信息（实际应该返回token）
        return jsonify({
            "success": True,
            "user": {
                "user_id": user['user_id'],
            }
        })

    except Exception as e:
        print(f"数据库错误: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# 日志配置
logging.basicConfig(filename='search.log', level=logging.INFO)


def log_search(func):
    """记录搜索日志的装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": request.json.get('query'),
            "params": request.json,
            "client_ip": request.remote_addr
        }
        logging.info(str(log_entry))
        return result

    return wrapper


# 记录搜索历史
def store_history(history_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_id = history_data["user_id"]
        words = history_data["words"]
        # 检查历史是否存在
        cursor.execute(
            "SELECT user_id FROM history WHERE user_id=%s AND words=%s",
            (user_id, words)
        )
        conflicts = cursor.fetchone()
        if not conflicts:
            cursor.execute(
                "INSERT INTO history (user_id,words) VALUES (%s,%s)",
                (user_id, words)
            )
        conn.commit()
        return jsonify({
            "success": True,
        })

    except Exception as e:
        print(f"数据库错误: {e}")
        return jsonify({"success": False, "message": "服务器错误"}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/api/search/<user_id>', methods=['POST'])
@log_search
def search(user_id):
    try:
        data = request.json
        query = data.get('query', '')

        # 记录历史
        history_data = {
            "user_id": user_id,
            "words": query
        }
        store_history(history_data)

        search_body = {
            "should": [],
            "filter": []
        }
        # 文档查询
        if data.get("file_type"):
            document_result = search_documents(query)
            return jsonify({
                "results": document_result,
                "type": "doc"
            })
        # 通配查询
        elif data.get('wildcard_type'):
            search_body = {
                "should": [
                    {
                        "wildcard": {
                            "title": {
                                "value": query
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "keywords": {
                                "value": query
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "content": {
                                "value": query
                            }
                        }
                    }
                ]
            }
        # 短语查询
        elif data.get("term_type"):
            search_body["should"].append({
                "multi_match": {
                    "query": query,  # 查询的短语
                    "fields": ["title", "keywords", "content"],  # 需要匹配的字段
                    "type": "phrase",  # 短语匹配类型
                    "analyzer": "ik_max_word"  # 使用 ik_max_word 分词器进行短语查询
                }
            })
        # 普通查询
        elif query:
            search_body["should"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "keywords^3", "content", "url"],
                    "type": "best_fields",
                    "analyzer": "ik_smart",
                }
            })
            # 个性化查询
            history_query=get_history(user_id).get_json()["history"][0]
            if history_query:
                search_body["should"].append({
                    "multi_match": {
                        "query": history_query,
                        "fields": ["title^3", "keywords^3", "content", "url"],
                        "type": "best_fields",
                        "analyzer": "ik_smart",
                        "boost": 0.1
                    }
                })

        print(search_body)
        # 执行搜索
        result = es.search(
            index=ES_INDEX,
            query={"bool": search_body},
            highlight={
                "fields": {
                    "content": {}
                },
                "pre_tags": ["<highlight>"],
                "post_tags": ["</highlight>"]
            },
            from_=(int(data.get('page', 1)) - 1) * int(data.get('size', 10)),
            size=int(data.get('size', 10)),
            sort=[{"timestamp": "desc"}] if data.get('sort') == 'date' else None
        )

        # 处理结果（保持不变）
        hits = []
        for hit in result['hits']['hits']:
            hits.append({
                "id": hit['_id'],
                "title": hit['_source'].get('title', ''),
                "url": hit['_source'].get('url', ''),
                "snippet": ''.join(hit.get('highlight', {}).get('content', [''])),
                "timestamp": hit['_source'].get('timestamp', ''),
                "content": hit['_source'].get('content', '')
            })


        return jsonify({
            "total": result['hits']['total']['value'],
            "results": hits,
            "type": "normal"
        })

    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/snapshot', methods=['POST'])
def get_snapshot():
    data = request.json
    image_name = data.get('img_name', '')
    print(image_name)
    try:
        # 指向 snapshot 文件夹中的 resized_snapshot_img
        image_path = '../snapshot/snapshot_img/' + image_name + '.png'

        # 打开图片
        webbrowser.open('file://' + os.path.abspath(image_path))
        print("完整路径:", os.path.abspath(image_path))
        return jsonify({"success": True, })

    except Exception as e:
        return jsonify({"success": False, 'error': str(e)}), 500


@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT words FROM history WHERE user_id = %s",
            (user_id,)
        )
        history = cursor.fetchall()
        search_history = []
        for record in history:
            if record['words']:
                search_history.extend(record['words'].split(','))
        return jsonify({"history": search_history})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# 在搜索接口后新增推荐功能
@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        current_doc_id = data.get('current_id')
        # 策略：基于搜索id的相关推荐
        if current_doc_id:
            suggest_result = es.search(
                index=ES_INDEX,
                query={
                    "more_like_this": {
                        "fields": ["title", "content", "keywords"],
                        "like": [{"_index": ES_INDEX, "_id": current_doc_id}],
                        "min_term_freq": 1,
                        "max_query_terms": 12,
                        "min_doc_freq": 1
                    }
                },
                size=5
            )
            return jsonify([hit['_source'] for hit in suggest_result['hits']['hits']])
        return jsonify([])

    except Exception as e:
        app.logger.error(f"推荐失败: {str(e)}")
        return jsonify([])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
