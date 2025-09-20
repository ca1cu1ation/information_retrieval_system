import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
from elasticsearch import Elasticsearch
from docx import Document
import fitz  # PyMuPDF
import pandas as pd

# 配置
DOWNLOAD_FOLDER = r"D:\searcher\lab4\Code\document"
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


def setup_index():
    """创建Elasticsearch索引（如果不存在）"""
    if not es.indices.exists(index=index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "file_name": {"type": "keyword"},
                    "content": {"type": "text", "analyzer": "ik_max_word"},
                    "file_path": {"type": "keyword"},
                    "download_url": {"type": "keyword"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        es.indices.create(index=index_name, body=mapping)


def download_file(url, save_path):
    """下载文件并保存到指定路径"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': urlparse(url).netloc
        }

        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            # 从Content-Disposition或URL中获取真实文件名
            filename = re.findall('filename="?(.+)"?',
                                  r.headers.get('Content-Disposition', ''))[0] \
                if 'Content-Disposition' in r.headers \
                else os.path.basename(urlparse(url).path)

            final_path = os.path.join(os.path.dirname(save_path), filename)

            with open(final_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"下载成功: {filename}")
            return final_path  # 返回实际存储路径

    except Exception as e:
        print(f"下载失败 {url} | 错误: {str(e)[:200]}")
        return None


def extract_content(file_path):
    """提取文档内容"""
    extension = os.path.splitext(file_path)[1].lower()
    content = ""

    try:
        if extension == ".docx":
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif extension == ".pdf":
            pdf = fitz.open(file_path)
            for page in pdf:
                content += page.get_text() + "\n"
            pdf.close()
        elif extension in [".xls", ".xlsx"]:
            df = pd.read_excel(file_path)
            content = df.to_string(index=False)
        else:
            print(f"不支持的文件类型: {extension}")
            return None
        return content.strip()
    except Exception as e:
        print(f"内容提取失败 {file_path}: {e}")
        return None


def index_document(file_path, download_url):
    """将单个文档索引到Elasticsearch"""
    content = extract_content(file_path)
    if not content:
        return False

    doc = {
        "file_name": os.path.basename(file_path),
        "content": content,
        "file_path": file_path,
        "download_url": download_url,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    try:
        es.index(index=index_name, document=doc)
        print(f"已索引: {file_path}")
        return True
    except Exception as e:
        print(f"索引失败 {file_path}: {e}")
        return False


def crawl_and_index(base_url, max_pages=5):
    """爬取文档并自动索引到Elasticsearch"""
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    setup_index()

    visited_urls = set()
    downloaded_files = set()
    current_url = base_url
    page_count = 0

    # 检查已索引的文件，避免重复处理
    existing_files = set()
    res = es.search(index=index_name, query={"match_all": {}}, size=1000)
    for hit in res['hits']['hits']:
        existing_files.add(hit['_source']['download_url'])

    while current_url and page_count < max_pages:
        if current_url in visited_urls:
            break
        visited_urls.add(current_url)

        print(f"\n正在爬取页面: {current_url}")

        try:
            response = requests.get(current_url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有文档链接
            doc_links = []
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                # 匹配常见文档格式（扩展更多格式可按需添加）
                if re.search(r'\.(pdf|docx?|xlsx?)$', href):
                    full_url = urljoin(current_url, a['href'])
                    # 去重并验证URL有效性
                    if full_url not in doc_links and not full_url.endswith(('#', '/')):
                        doc_links.append(full_url)

            # 下载并索引文档
            for doc_url in doc_links:
                if doc_url in existing_files:
                    print(f"已跳过（已索引）: {doc_url}")
                    continue

                filename = os.path.basename(doc_url)
                save_path = os.path.join(DOWNLOAD_FOLDER, filename)

                if download_file(doc_url, save_path):
                    if index_document(save_path, doc_url):
                        downloaded_files.add(doc_url)
                    else:
                        # 索引失败时删除下载的文件
                        if os.path.exists(save_path):
                            os.remove(save_path)

                time.sleep(1)  # 礼貌延迟

            # 查找下一页
            current_url = find_next_page(current_url,soup)
            page_count += 1

        except Exception as e:
            print(f"页面爬取失败: {current_url} | 错误: {e}")
            break


def find_next_page(current_url,soup):
    """查找下一页URL（针对/list1.htm格式的分页）"""
    # 使用正则表达式匹配URL中的数字部分
    """从网页中解析分页导航栏的下一个链接"""
    # 查找常见的分页元素（根据目标网站调整选择器）
    next_btn = soup.select_one('a.next, .pagination a:contains("下一页")')
    if next_btn and next_btn.get('href'):
        return urljoin(current_url, next_btn['href'])

    # 如果找不到明确的下页按钮，尝试数字分页
    pagination = soup.select('.pagination a[href*="page="]')
    if pagination:
        return urljoin(current_url, pagination[-1]['href'])

    return None


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
                "file_path": source['file_path'],
                "url": source['download_url'],
                "content": source['content'][:200] + "...",
                "highlight": hit.get('highlight', {}).get('content', [])
            })
        return search_results
    except Exception as e:
        print(f"搜索失败: {e}")
        return []


if __name__ == "__main__":
    # 示例URL（替换为实际目标URL）
    base_url = "https://www.nankai.edu.cn/157/list1.htm"
    # 爬取并索引文档
    crawl_and_index(base_url, max_pages=20)
