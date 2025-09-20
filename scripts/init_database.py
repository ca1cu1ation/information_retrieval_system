#!/usr/bin/env python3
"""
Database initialization script for Information Retrieval System
数据库初始化脚本
"""

import mysql.connector
from mysql.connector import Error
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def create_database():
    """创建数据库和表"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = mysql.connector.connect(
            host=Config.MYSQL_CONFIG['host'],
            user=Config.MYSQL_CONFIG['user'],
            password=Config.MYSQL_CONFIG['password'],
            port=Config.MYSQL_CONFIG['port']
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        database_name = Config.MYSQL_CONFIG['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 {database_name} 创建成功")
        
        # 使用数据库
        cursor.execute(f"USE {database_name}")
        
        # 读取并执行SQL脚本
        script_path = os.path.join(os.path.dirname(__file__), '..', 'database_schema.sql')
        with open(script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # 分割并执行每个SQL语句
        statements = sql_script.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
        
        connection.commit()
        print("✓ 数据库表创建成功")
        
        # 验证表是否创建成功
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ 已创建 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
            
    except Error as e:
        print(f"✗ 数据库操作失败: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def test_connection():
    """测试数据库连接"""
    try:
        connection = mysql.connector.connect(**Config.MYSQL_CONFIG)
        cursor = connection.cursor()
        
        # 测试查询
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ MySQL 连接成功，版本: {version[0]}")
        
        # 检查表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✓ 发现 {len(tables)} 个表")
            return True
        else:
            print("✗ 未发现任何表")
            return False
            
    except Error as e:
        print(f"✗ 数据库连接失败: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """主函数"""
    print("=== 数据库初始化脚本 ===")
    
    # 首先测试连接
    print("\n1. 测试数据库连接...")
    if test_connection():
        print("数据库已经初始化，跳过创建步骤")
        return
    
    # 创建数据库和表
    print("\n2. 创建数据库和表...")
    if create_database():
        print("\n3. 验证创建结果...")
        test_connection()
        print("\n✓ 数据库初始化完成！")
    else:
        print("\n✗ 数据库初始化失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()