# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

这是一个基于 Flask 的 Web 应用，用于爬取和管理小红书内容。提供 REST API 用于爬取笔记、管理用户和存储爬取的数据。

## 启动应用

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行开发服务器
python run.py

# 默认运行在 http://localhost:8000（在 .env.dev 中配置）
```

## 数据库迁移

```bash
# 创建新迁移
flask db migrate -m "迁移说明"

# 执行迁移
flask db upgrade

# 回滚
flask db downgrade
```

## 架构

### 爬虫系统 (`app/spider/`)

爬虫采用抽象基类模式，配合管道处理流程：

- `core/base_spider.py` - 抽象基类 `BaseSpider`，定义爬取接口（`start_requests`、`parse`、`download`）
- `core/post_media_spider.py` - 小红书笔记的具体实现
- `scheduler.py` - `SpiderScheduler` 单例，同步执行爬虫
- `pipelines.py` - 两级管道：`PostCleaningPipeline`（数据清洗）→ `PostDatabasePipeline`（存储）
- `utils.py` - URL 提取和验证工具

爬虫通过解析 `<script>` 标签中的 `window.__INITIAL_STATE__` 来提取小红书页面数据。

### API 层 (`app/api/`)

基于 Flask-RESTful 的 RESTful API：

- `resources/spider.py` - 爬虫接口（`SpiderListAPI`、`SpiderDetailAPI`）
- `resources/user.py` - 用户认证接口（注册、登录、登出、列表）
- `models/` - SQLAlchemy 模型（PostDetail、PostMedia、PostInteract、PostTag、PostUser、User、RevokedToken）
- `response.py` - 统一响应格式（`send_success`、`send_error`、`send_server_error`）

### 数据库模型

笔记数据拆分到多个关联模型中：
- `PostDetailModel` - 笔记正文、标签
- `PostMediaModel` - 图片/视频
- `PostInteractModel` - 点赞、评论、收藏
- `PostUserModel` - 作者信息
- `PostTagModel` - 标签详情

### 认证

基于 JWT 的认证机制，支持 token 黑名单。`RevokedTokenModel` 存储已撤销的 JTI，`check_if_token_in_blacklist` 钩子拦截无效或过期的 token 请求。

### 配置 (`app/config.py`)

环境驱动的配置：支持 `development`、`production`、`testing` 三种模式。数据库 URI 由环境变量构建（`MYSQL_USER_NAME`、`MYSQL_USER_PASSWORD`、`MYSQL_HOSTNAME` 等）。

### 媒体存储

下载的文件存储在 `storage/` 目录下，按日期分子目录。`MEDIA_DIR` 配置指定根路径。

## 核心 API 接口

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/spider` | 爬取小红书笔记（body: `{"content": "<url 或页面文本>"}`） |
| GET | `/api/spider` | 获取所有已爬取的笔记列表 |
| GET | `/api/spider/<post_id>` | 获取笔记详情 |
| DELETE | `/api/spider/<post_id>` | 删除笔记 |
| POST | `/api/user` | 注册新用户 |
| POST | `/api/user/login` | 登录（返回 JWT） |
| POST | `/api/user/logout` | 登出（token 加入黑名单） |

## 依赖

Flask 生态（Flask-SQLAlchemy、Flask-JWT-Extended、Flask-Migrate）、BeautifulSoup4（HTML 解析）、SQLAlchemy 2.0 + PyMySQL（数据库）、Pillow（图片处理）、Loguru（日志）。
