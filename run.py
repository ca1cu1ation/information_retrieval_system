#!/usr/bin/env python3
"""
System startup script for Information Retrieval System
系统启动脚本
"""

import os
import sys
import time
import subprocess
import signal
import atexit
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，正在关闭服务...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """清理所有进程"""
        print("正在关闭所有服务...")
        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"关闭 {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def start_service(self, name, command, cwd=None):
        """启动服务"""
        try:
            print(f"启动 {name}...")
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            self.processes[name] = process
            
            # 等待一下确保服务启动
            time.sleep(2)
            
            if process.poll() is None:
                print(f"✓ {name} 启动成功 (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"✗ {name} 启动失败:")
                print(f"  stdout: {stdout.decode()}")
                print(f"  stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"✗ {name} 启动异常: {e}")
            return False
    
    def check_service_status(self, name):
        """检查服务状态"""
        if name in self.processes:
            process = self.processes[name]
            if process.poll() is None:
                return True
        return False
    
    def monitor_services(self):
        """监控服务状态"""
        while self.running:
            try:
                time.sleep(10)
                for name in list(self.processes.keys()):
                    if not self.check_service_status(name):
                        print(f"⚠ 服务 {name} 已停止")
                        
            except KeyboardInterrupt:
                break

def check_dependencies():
    """检查依赖服务"""
    print("检查依赖服务...")
    
    # 检查 MySQL
    try:
        import mysql.connector
        conn = mysql.connector.connect(**Config.MYSQL_CONFIG)
        conn.close()
        print("✓ MySQL 连接正常")
    except Exception as e:
        print(f"✗ MySQL 连接失败: {e}")
        return False
    
    # 检查 Elasticsearch
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(**Config.get_elasticsearch_config())
        if es.ping():
            print("✓ Elasticsearch 连接正常")
        else:
            print("✗ Elasticsearch 连接失败")
            return False
    except Exception as e:
        print(f"✗ Elasticsearch 连接异常: {e}")
        return False
    
    return True

def check_indices():
    """检查索引是否存在"""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(**Config.get_elasticsearch_config())
        
        indices = [Config.NEWS_INDEX, Config.DOCUMENTS_INDEX]
        missing_indices = []
        
        for index in indices:
            if not es.indices.exists(index=index):
                missing_indices.append(index)
        
        if missing_indices:
            print(f"⚠ 缺少索引: {', '.join(missing_indices)}")
            print("请运行: python scripts/init_elasticsearch.py")
            return False
        
        print("✓ 所有索引都存在")
        return True
        
    except Exception as e:
        print(f"✗ 检查索引失败: {e}")
        return False

def start_development_server():
    """启动开发服务器"""
    manager = ServiceManager()
    
    print("=== 信息检索系统启动 ===")
    
    # 检查依赖
    if not check_dependencies():
        print("依赖检查失败，请确保 MySQL 和 Elasticsearch 正在运行")
        return
    
    # 检查索引
    if not check_indices():
        print("索引检查失败，请先初始化 Elasticsearch 索引")
        return
    
    # 启动 Flask 应用
    flask_cmd = f"{sys.executable} Code/server/app.py"
    if manager.start_service("Flask应用", flask_cmd):
        print(f"✓ Web服务已启动: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    # 启动文件服务器（用于提供静态文件）
    try:
        import http.server
        import socketserver
        
        # 在后台启动简单的HTTP服务器
        web_cmd = f"{sys.executable} -m http.server 8080 --directory Code/web"
        if manager.start_service("静态文件服务", web_cmd):
            print("✓ 静态文件服务已启动: http://localhost:8080")
    except:
        print("⚠ 静态文件服务启动失败，请手动访问 HTML 文件")
    
    print("\n=== 服务启动完成 ===")
    print("访问地址:")
    print(f"- 搜索界面: http://localhost:8080/html/searcher.html")
    print(f"- 登录界面: http://localhost:8080/html/login.html")
    print(f"- API 服务: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print("\n按 Ctrl+C 停止所有服务")
    
    # 监控服务
    try:
        manager.monitor_services()
    except KeyboardInterrupt:
        print("\n收到停止信号...")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            # 初始化系统
            print("初始化系统...")
            
            # 初始化数据库
            print("\n1. 初始化数据库...")
            os.system(f"{sys.executable} scripts/init_database.py")
            
            # 初始化 Elasticsearch
            print("\n2. 初始化 Elasticsearch...")
            os.system(f"{sys.executable} scripts/init_elasticsearch.py")
            
            print("\n✓ 系统初始化完成")
            
        elif command == "crawl":
            # 运行爬虫
            print("启动爬虫...")
            os.system(f"{sys.executable} Code/spider/nankai_news.py")
            
        elif command == "index":
            # 创建索引
            print("创建搜索索引...")
            os.system(f"{sys.executable} Code/index/index.py")
            
        elif command == "snapshot":
            # 生成快照
            print("生成网页快照...")
            os.system(f"{sys.executable} Code/snapshot/snapshot.py")
            
        else:
            print(f"未知命令: {command}")
            print("可用命令: init, crawl, index, snapshot")
    else:
        # 启动开发服务器
        start_development_server()

if __name__ == "__main__":
    main()