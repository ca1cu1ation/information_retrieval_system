#!/usr/bin/env python3
"""
Elasticsearch initialization script for Information Retrieval System
Elasticsearch 初始化脚本
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from config import Config
from elasticsearch_config import (
    NEWS_INDEX_SETTINGS, NEWS_INDEX_MAPPINGS,
    DOCUMENTS_INDEX_SETTINGS, DOCUMENTS_INDEX_MAPPINGS
)

def test_elasticsearch_connection():
    """测试 Elasticsearch 连接"""
    try:
        es = Elasticsearch(**Config.get_elasticsearch_config())
        
        if es.ping():
            info = es.info()
            print(f"✓ Elasticsearch 连接成功")
            print(f"  版本: {info['version']['number']}")
            print(f"  集群名: {info['cluster_name']}")
            return es
        else:
            print("✗ Elasticsearch 连接失败")
            return None
    except Exception as e:
        print(f"✗ Elasticsearch 连接异常: {e}")
        return None

def create_index(es, index_name, settings, mappings):
    """创建索引"""
    try:
        # 检查索引是否已存在
        if es.indices.exists(index=index_name):
            print(f"⚠ 索引 {index_name} 已存在，是否删除重建？(y/N): ", end='')
            choice = input().lower()
            if choice == 'y':
                es.indices.delete(index=index_name)
                print(f"✓ 已删除索引 {index_name}")
            else:
                print(f"跳过索引 {index_name}")
                return True
        
        # 创建索引
        es.indices.create(
            index=index_name,
            settings=settings,
            mappings=mappings
        )
        print(f"✓ 索引 {index_name} 创建成功")
        return True
        
    except Exception as e:
        print(f"✗ 创建索引 {index_name} 失败: {e}")
        return False

def verify_index(es, index_name):
    """验证索引"""
    try:
        # 获取索引信息
        index_info = es.indices.get(index=index_name)
        mappings = index_info[index_name]['mappings']
        settings = index_info[index_name]['settings']
        
        print(f"✓ 索引 {index_name} 验证成功")
        print(f"  字段数量: {len(mappings.get('properties', {}))}")
        print(f"  分片数: {settings['index']['number_of_shards']}")
        print(f"  副本数: {settings['index']['number_of_replicas']}")
        
        return True
    except Exception as e:
        print(f"✗ 验证索引 {index_name} 失败: {e}")
        return False

def check_ik_plugin(es):
    """检查 IK 分词插件"""
    try:
        # 测试 IK 分词器
        test_text = "中华人民共和国"
        response = es.indices.analyze(
            analyzer="ik_max_word",
            text=test_text
        )
        
        tokens = [token['token'] for token in response['tokens']]
        print(f"✓ IK 分词插件工作正常")
        print(f"  测试文本: {test_text}")
        print(f"  分词结果: {', '.join(tokens)}")
        return True
        
    except Exception as e:
        print(f"✗ IK 分词插件测试失败: {e}")
        print("请确保已安装 elasticsearch-analysis-ik 插件")
        return False

def main():
    """主函数"""
    print("=== Elasticsearch 初始化脚本 ===")
    
    # 测试连接
    print("\n1. 测试 Elasticsearch 连接...")
    es = test_elasticsearch_connection()
    if not es:
        print("请确保 Elasticsearch 服务正在运行")
        sys.exit(1)
    
    # 检查 IK 分词插件
    print("\n2. 检查 IK 分词插件...")
    if not check_ik_plugin(es):
        print("警告: IK 分词插件未正确安装，中文搜索可能受到影响")
    
    # 创建新闻索引
    print(f"\n3. 创建新闻索引 ({Config.NEWS_INDEX})...")
    if create_index(es, Config.NEWS_INDEX, NEWS_INDEX_SETTINGS, NEWS_INDEX_MAPPINGS):
        verify_index(es, Config.NEWS_INDEX)
    
    # 创建文档索引
    print(f"\n4. 创建文档索引 ({Config.DOCUMENTS_INDEX})...")
    if create_index(es, Config.DOCUMENTS_INDEX, DOCUMENTS_INDEX_SETTINGS, DOCUMENTS_INDEX_MAPPINGS):
        verify_index(es, Config.DOCUMENTS_INDEX)
    
    print("\n✓ Elasticsearch 初始化完成！")
    print("\n下一步:")
    print("- 运行数据导入脚本: python Code/index/index.py")
    print("- 运行爬虫脚本: python Code/spider/nankai_news.py")

if __name__ == "__main__":
    main()