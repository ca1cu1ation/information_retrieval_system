-- 创建数据库
CREATE DATABASE IF NOT EXISTS web_search CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE web_search;

-- 创建新闻表
CREATE TABLE IF NOT EXISTS nankai_news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ctime DATETIME NOT NULL COMMENT '发稿时间',
    url VARCHAR(500) NOT NULL COMMENT '新闻链接',
    wapurl VARCHAR(500) COMMENT '移动端链接',
    title VARCHAR(500) NOT NULL COMMENT '新闻标题',
    media_name VARCHAR(100) COMMENT '媒体名称',
    keywords TEXT COMMENT '关键词',
    content LONGTEXT COMMENT '新闻内容',
    page_link TEXT COMMENT '相关链接',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title(255)),
    INDEX idx_ctime (ctime),
    INDEX idx_keywords (keywords(255)),
    FULLTEXT INDEX ft_content (content),
    FULLTEXT INDEX ft_title (title),
    UNIQUE KEY unique_url (url(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='南开新闻表';

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 创建搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    query TEXT NOT NULL COMMENT '搜索关键词',
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '搜索时间',
    INDEX idx_user_id (user_id),
    INDEX idx_search_time (search_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搜索历史表';

-- 创建搜索日志表
CREATE TABLE IF NOT EXISTS search_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) COMMENT '用户ID',
    query TEXT NOT NULL COMMENT '搜索查询',
    params JSON COMMENT '搜索参数',
    client_ip VARCHAR(45) COMMENT '客户端IP',
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '搜索时间',
    response_time INT COMMENT '响应时间(毫秒)',
    result_count INT COMMENT '结果数量',
    INDEX idx_user_id (user_id),
    INDEX idx_search_time (search_time),
    INDEX idx_client_ip (client_ip)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搜索日志表';

-- 插入示例用户
INSERT IGNORE INTO users (username, password, email) VALUES 
('admin', 'admin123', 'admin@example.com'),
('testuser', 'test123', 'test@example.com');

-- 创建额外表（根据代码中的引用）
CREATE TABLE IF NOT EXISTS nankai_news_mtnk (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL COMMENT '标题',
    url VARCHAR(500) NOT NULL COMMENT '链接',
    content LONGTEXT COMMENT '内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_url (url(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='南开新闻移动端表';