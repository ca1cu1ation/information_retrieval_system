# 快速开始指南

本指南将帮助您在 10 分钟内启动并运行信息检索系统。

## 🚀 最快启动方式 (Docker)

如果您的系统已安装 Docker 和 Docker Compose：

```bash
# 1. 克隆项目
git clone https://github.com/ca1cu1ation/information_retrieval_system.git
cd information_retrieval_system

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务启动 (约1-2分钟)
docker-compose logs -f

# 4. 访问应用
# 搜索界面: http://localhost
# API服务: http://localhost:3000
# Elasticsearch管理: http://localhost:5601
```

## 🔧 手动安装方式

### 前提条件
- Python 3.9+
- MySQL 8.0+  
- Elasticsearch 8.x

### 步骤

1. **克隆项目**
```bash
git clone https://github.com/ca1cu1ation/information_retrieval_system.git
cd information_retrieval_system
```

2. **运行自动安装脚本**
```bash
./setup.sh
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库密码等配置
nano .env
```

4. **初始化系统**
```bash
python run.py init
```

5. **启动服务**
```bash
python run.py
```

## 📱 第一次使用

1. **访问搜索界面**
   - 打开浏览器访问: http://localhost:8080/html/searcher.html

2. **登录系统** (可选)
   - 访问: http://localhost:8080/html/login.html
   - 测试账号: admin / admin123

3. **进行搜索**
   - 输入关键词如 "南开大学"
   - 点击搜索按钮

4. **高级功能**
   - 点击"高级搜索"尝试不同搜索类型
   - 使用通配符: "南开*" 或 "?大学"
   - 按文档类型筛选

## 🔍 示例搜索

- **普通搜索**: `南开大学`
- **短语搜索**: `"人工智能"`
- **通配符搜索**: `北京*大学`
- **文档搜索**: 选择"PDF"类型搜索

## 📊 填充数据

如果没有搜索结果，需要先填充一些数据：

```bash
# 爬取新闻数据
python run.py crawl

# 创建搜索索引
python run.py index

# 生成网页快照 (可选)
python run.py snapshot
```

## 🆘 常见问题

**Q: 搜索没有结果？**
A: 运行 `python run.py crawl` 爬取数据，然后运行 `python run.py index` 创建索引

**Q: 中文搜索不准确？**
A: 确保 Elasticsearch 已安装 IK 分词插件：
```bash
elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v8.8.2/elasticsearch-analysis-ik-8.8.2.zip
```

**Q: 无法连接数据库？**
A: 检查 MySQL 是否运行，确认 `.env` 中的密码配置

**Q: Elasticsearch 连接失败？**
A: 确保 Elasticsearch 在 9200 端口运行，可通过 `curl localhost:9200` 测试

## 🎯 下一步

- 查看完整的 [README.md](README.md) 了解详细功能
- 探索 API 接口进行自定义开发
- 配置自动化爬虫定期更新数据
- 部署到生产环境

## 📞 需要帮助？

- 查看详细文档: [README.md](README.md)
- 提交问题: https://github.com/ca1cu1ation/information_retrieval_system/issues
- 参与讨论: https://github.com/ca1cu1ation/information_retrieval_system/discussions