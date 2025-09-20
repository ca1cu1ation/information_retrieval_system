#!/bin/bash

# Information Retrieval System Setup Script
# 信息检索系统安装脚本

set -e

echo "=== 信息检索系统安装脚本 ==="
echo "正在开始安装..."

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "错误: 需要 Python 3.9 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "Python 版本检查通过: $python_version"

# 检查并安装系统依赖
echo "检查系统依赖..."

# 检查 MySQL
if ! command -v mysql &> /dev/null; then
    echo "警告: 未检测到 MySQL，请手动安装 MySQL 8.0+"
fi

# 检查 Elasticsearch
if ! curl -s "localhost:9200" &> /dev/null; then
    echo "警告: 未检测到 Elasticsearch，请确保 Elasticsearch 正在运行"
fi

# 创建虚拟环境
echo "创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装 Python 依赖
echo "安装 Python 依赖包..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p documents
mkdir -p snapshots
mkdir -p logs
mkdir -p Code/snapshot/snapshot_img

# 复制配置文件
echo "配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建 .env 配置文件，请根据需要修改配置"
fi

# 下载 ChromeDriver (用于快照功能)
echo "配置 ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "下载 ChromeDriver..."
    
    # 检测系统架构
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
        unzip /tmp/chromedriver.zip -d /tmp/
        sudo mv /tmp/chromedriver /usr/local/bin/
        sudo chmod +x /usr/local/bin/chromedriver
        rm /tmp/chromedriver.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install chromedriver
    else
        echo "请手动安装 ChromeDriver"
    fi
fi

# 测试数据库连接
echo "测试数据库连接..."
python3 -c "
import mysql.connector
from config import Config

try:
    conn = mysql.connector.connect(**Config.MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    cursor.close()
    conn.close()
    print('✓ MySQL 连接成功')
except Exception as e:
    print(f'✗ MySQL 连接失败: {e}')
    print('请检查 MySQL 服务状态和配置')
"

# 测试 Elasticsearch 连接
echo "测试 Elasticsearch 连接..."
python3 -c "
from elasticsearch import Elasticsearch
from config import Config

try:
    es = Elasticsearch(**Config.get_elasticsearch_config())
    if es.ping():
        print('✓ Elasticsearch 连接成功')
    else:
        print('✗ Elasticsearch 连接失败')
except Exception as e:
    print(f'✗ Elasticsearch 连接失败: {e}')
    print('请检查 Elasticsearch 服务状态')
"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "下一步操作："
echo "1. 修改 .env 文件中的配置（特别是数据库密码）"
echo "2. 初始化数据库: mysql -u root -p < database_schema.sql"
echo "3. 创建搜索索引: cd Code/index && python index.py"
echo "4. 启动服务: cd Code/server && python app.py"
echo "5. 访问 http://localhost:3000"
echo ""
echo "可选步骤："
echo "- 运行爬虫: cd Code/spider && python nankai_news.py"
echo "- 生成快照: cd Code/snapshot && python snapshot.py"
echo ""
echo "如需帮助，请查看 README.md 或提交 Issue"