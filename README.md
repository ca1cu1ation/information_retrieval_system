# 信息检索系统 (Information Retrieval System)

一个基于 Flask + Elasticsearch + MySQL 的智能信息检索系统，支持新闻搜索、文档检索、网页快照和个性化推荐功能。

## 🌟 功能特性

### 核心功能
- **全文搜索**: 基于 Elasticsearch 的高性能全文搜索引擎
- **多格式文档支持**: 支持 PDF、Word、Excel 等文档格式的内容提取和搜索
- **智能分词**: 使用 IK 分词器支持中文分词和搜索
- **网页快照**: 自动生成和查看网页快照功能
- **用户系统**: 用户登录、搜索历史记录
- **个性化推荐**: 基于用户搜索历史的智能推荐

### 搜索功能
- **普通搜索**: 支持关键词全文搜索
- **短语搜索**: 精确短语匹配搜索
- **通配符搜索**: 支持前缀和后缀通配符搜索
- **文档类型过滤**: 按文件类型（PDF、Word、Excel）筛选
- **高级搜索**: 多条件组合搜索
- **搜索高亮**: 搜索结果关键词高亮显示

### 数据来源
- **南开大学新闻**: 自动爬取南开大学官网新闻内容
- **文档库**: 支持上传和索引各类文档
- **网页快照**: 自动保存网页截图

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Flask Backend  │    │  Elasticsearch  │
│   (HTML/CSS/JS) │◄──►│    (Python)     │◄──►│   (Search)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │      MySQL      │
                       │   (Database)    │
                       └─────────────────┘
```

### 技术栈
- **后端**: Python 3.9+, Flask, Elasticsearch 8.x
- **数据库**: MySQL 8.0, Elasticsearch
- **前端**: HTML5, CSS3, JavaScript (原生)
- **爬虫**: Selenium, BeautifulSoup4, Requests
- **文档处理**: PyMuPDF, python-docx, pandas
- **中文分词**: jieba, Elasticsearch IK Plugin

## 📋 系统要求

### 软件依赖
- Python 3.9+
- MySQL 8.0+
- Elasticsearch 8.x
- Chrome/Chromium 浏览器 (用于网页快照)
- ChromeDriver

### 硬件要求
- 内存: 4GB+ 推荐
- 存储: 10GB+ 可用空间
- CPU: 2核+ 推荐

## 🚀 快速开始

### 方式一：使用 Docker (推荐)

1. **克隆项目**
```bash
git clone https://github.com/ca1cu1ation/information_retrieval_system.git
cd information_retrieval_system
```

2. **启动所有服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 搜索界面: http://localhost
- API 服务: http://localhost:3000
- Kibana (ES管理): http://localhost:5601

### 方式二：手动安装

#### 1. 环境准备

**安装 Python 依赖**
```bash
pip install -r requirements.txt
```

**安装 Elasticsearch IK 分词插件**
```bash
# 下载并安装 IK 分词插件
elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.8.2/elasticsearch-analysis-ik-8.8.2.zip
```

#### 2. 数据库配置

**MySQL 设置**
```bash
# 登录 MySQL
mysql -u root -p

# 执行数据库初始化脚本
source database_schema.sql
```

**Elasticsearch 设置**
```bash
# 启动 Elasticsearch
./bin/elasticsearch

# 验证运行状态
curl -X GET "localhost:9200/"
```

#### 3. 配置文件

**复制并配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等配置
```

**主要配置项**:
- `MYSQL_PASSWORD`: MySQL 数据库密码
- `ELASTICSEARCH_USERNAME/PASSWORD`: ES 认证信息（可选）
- `DOWNLOAD_FOLDER`: 文档下载存储路径
- `SNAPSHOT_FOLDER`: 网页快照存储路径

#### 4. 启动服务

**启动 Flask 应用**
```bash
cd Code/server
python app.py
```

**建立搜索索引**
```bash
cd Code/index
python index.py
```

**启动爬虫 (可选)**
```bash
cd Code/spider
python nankai_news.py  # 爬取新闻
python docment.py      # 爬取文档
```

**生成网页快照 (可选)**
```bash
cd Code/snapshot
python snapshot.py
```

## 🔧 配置说明

### 数据库配置
在 `config.py` 或 `.env` 文件中配置数据库连接：

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'your_password',
    'database': 'web_search'
}
```

### Elasticsearch 配置
配置 Elasticsearch 连接和索引设置：

```python
ELASTICSEARCH_CONFIG = {
    'host': 'localhost',
    'port': 9200,
    'username': '',  # 可选
    'password': ''   # 可选
}
```

### 索引配置
系统使用两个主要索引：
- `news_index`: 新闻内容索引
- `documents_index`: 文档内容索引

## 📁 项目结构

```
information_retrieval_system/
├── Code/
│   ├── web/                    # 前端文件
│   │   ├── html/              # HTML 页面
│   │   ├── css/               # 样式文件
│   │   └── js/                # JavaScript 脚本
│   ├── server/                 # 后端服务
│   │   ├── app.py             # Flask 主应用
│   │   └── document_search.py # 文档搜索模块
│   ├── spider/                 # 网络爬虫
│   │   ├── nankai_news.py     # 新闻爬虫
│   │   └── docment.py         # 文档爬虫
│   ├── index/                  # 索引管理
│   │   └── index.py           # 索引创建和数据导入
│   └── snapshot/               # 快照功能
│       └── snapshot.py        # 网页快照生成
├── config.py                   # 配置文件
├── requirements.txt            # Python 依赖
├── database_schema.sql         # 数据库结构
├── docker-compose.yml          # Docker 配置
├── Dockerfile                  # Docker 构建文件
└── README.md                   # 项目说明
```

## 🔌 API 接口

### 搜索接口
```
POST /api/search/<user_id>
Content-Type: application/json

{
    "query": "搜索关键词",
    "page": 1,
    "size": 10,
    "file_type": "pdf",        // 可选：文件类型过滤
    "wildcard_type": true,     // 可选：通配符搜索
    "phrase_query": true       // 可选：短语搜索
}
```

### 搜索历史
```
GET /api/history/<user_id>
```

### 推荐接口
```
POST /api/recommend
Content-Type: application/json

{
    "user_id": "用户ID",
    "count": 5
}
```

### 快照接口
```
POST /api/snapshot
Content-Type: application/json

{
    "img_name": "快照名称"
}
```

## 🎯 使用指南

### 基本搜索
1. 访问 http://localhost/searcher.html
2. 在搜索框中输入关键词
3. 点击"搜索"按钮查看结果

### 高级搜索
1. 点击"高级搜索"展开选项
2. 选择搜索类型：
   - **短语搜索**: 精确匹配整个短语
   - **通配符搜索**: 使用 * 或 ? 进行模糊匹配
   - **文档类型**: 筛选特定格式的文档
3. 设置每页显示数量和排序方式

### 查看快照
在搜索结果中点击"查看快照"按钮，查看网页的历史截图。

### 个性化功能
- 系统会自动记录您的搜索历史
- 基于历史记录提供相关推荐
- 支持用户登录和个人设置

## 🛠️ 开发指南

### 添加新的数据源
1. 在 `Code/spider/` 目录下创建新的爬虫脚本
2. 实现数据抓取和清洗逻辑
3. 调用索引接口将数据存入 Elasticsearch

### 自定义搜索算法
1. 修改 `Code/server/app.py` 中的搜索逻辑
2. 调整 Elasticsearch 查询参数
3. 实现自定义评分和排序规则

### 扩展文档类型支持
1. 在 `Code/spider/docment.py` 中添加新的文档解析器
2. 更新 `extract_content` 函数
3. 配置相应的 MIME 类型处理

## 🐛 故障排除

### 常见问题

**1. Elasticsearch 连接失败**
- 检查 ES 服务是否正常启动
- 验证配置文件中的连接参数
- 确认网络连接和防火墙设置

**2. 中文分词不生效**
- 确认已安装 IK 分词插件
- 重启 Elasticsearch 服务
- 检查索引映射配置

**3. 爬虫无法正常工作**
- 检查 ChromeDriver 是否正确安装
- 确认目标网站是否可访问
- 查看错误日志排查具体问题

**4. 数据库连接问题**
- 验证 MySQL 服务状态
- 检查用户权限和密码
- 确认数据库和表是否正确创建

### 日志查看
```bash
# 查看应用日志
tail -f search.log

# 查看 Elasticsearch 日志
tail -f /var/log/elasticsearch/elasticsearch.log

# 查看 MySQL 日志
tail -f /var/log/mysql/error.log
```

## 📈 性能优化

### Elasticsearch 优化
- 调整分片和副本数量
- 配置合适的内存设置
- 使用合适的分词器和分析器

### 数据库优化
- 添加合适的索引
- 优化查询语句
- 配置连接池

### 应用优化
- 启用查询缓存
- 实现分页查询
- 使用异步处理长时间任务

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目作者: ca1cu1ation
- 项目链接: https://github.com/ca1cu1ation/information_retrieval_system

## 🙏 致谢

- [Elasticsearch](https://www.elastic.co/) - 强大的搜索和分析引擎
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 应用框架
- [IK Analysis](https://github.com/medcl/elasticsearch-analysis-ik) - 中文分词插件
- [南开大学](https://www.nankai.edu.cn/) - 数据源提供

---

⭐ 如果这个项目对您有帮助，请给我们一个 Star！