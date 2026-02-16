# 任务管理API - 部署指南

本项目是一个基于 FastAPI 的任务管理后端服务，适合部署到 Render、Replit 等免费服务器。

## 📁 文件结构

```
deploy/
├── main.py              # API主文件
├── requirements.txt     # Python依赖
├── .gitignore          # Git忽略文件
└── README.md           # 本文件
```

## 🚀 本地测试

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python main.py
```

### 3. 访问API
- 服务地址: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 🔌 API接口

### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/get-time` | 获取服务器时间 |
| GET | `/health` | 健康检查 |
| POST | `/login` | 登录 |

### 任务接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{user_id}` | 获取任务列表 |
| GET | `/api/tasks/{user_id}/today` | 今日任务 |
| GET | `/api/tasks/{user_id}/todo` | 待办任务 |
| GET | `/api/tasks/{user_id}/done` | 已完成任务 |
| GET | `/api/tasks/{user_id}/date/{task_date}` | 按日期查询 |

### 测试账号

| 用户名 | 密码 | user_id |
|--------|------|---------|
| admin | 123456 | user-001 |
| test | test123 | user-002 |

## 📦 部署到 Replit

### 方法一：通过 GitHub 导入（推荐）

1. **创建 GitHub 仓库**
   - 在 GitHub 上新建一个仓库
   - 将 `deploy/` 文件夹下的所有文件上传到仓库

2. **注册 Replit**
   - 访问 https://replit.com
   - 注册账号并登录

3. **导入项目**
   - 点击左上角 "Import" 按钮
   - 选择 "From GitHub"
   - 选择你刚创建的仓库
   - 点击 "Import" 导入

4. **配置运行命令**
   - Replit 会自动识别 Python 项目
   - 确认运行命令为: `python main.py`

5. **启动服务**
   - 点击顶部的 "Run" 按钮
   - 等待服务启动

6. **获取公网地址**
   - 点击地址栏左侧的 "Webview" 或 "Open in new tab"
   - 复制显示的 URL（类似 `https://xxx.replit.dev`）

### 方法二：直接在 Replit 创建

1. 新建 Replit 项目，选择 Python 模板
2. 将 `main.py` 和 `requirements.txt` 的内容复制进去
3. 点击 "Run" 运行

## 🌐 部署到 Render

### 1. 准备 GitHub 仓库

将 `deploy/` 文件夹下的文件推送到 GitHub 仓库。

### 2. 注册 Render

访问 https://render.com 并注册账号。

### 3. 创建 Web Service

1. 点击 "New +" → "Web Service"
2. 连接你的 GitHub 账号
3. 选择包含代码的仓库
4. 配置项目：
   - **Name**: 你的服务名称
   - **Region**: 选择就近地区
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Plan**: 选择免费的 Free 计划

5. 点击 "Create Web Service"

### 4. 配置环境变量（可选）

如果需要连接真实的 MySQL 数据库，可以在 Render 的 Environment 页面添加环境变量：

- `MYSQL_HOST`: 你的MySQL主机
- `MYSQL_PORT`: 端口（默认3306）
- `MYSQL_USER`: 用户名
- `MYSQL_PASSWORD`: 密码
- `MYSQL_DATABASE`: 数据库名

### 5. 等待部署完成

Render 会自动构建和部署，完成后会显示一个公网 URL（类似 `https://xxx.onrender.com`）。

## 🔧 配置说明

### 模拟数据模式

默认情况下，如果无法连接到 MySQL 数据库，API 会自动使用模拟数据，方便测试。

### 连接真实数据库

要连接你的真实 MySQL 数据库，需要：

1. 确保数据库可以从外网访问（或部署在同一内网）
2. 在 Render/Replit 上配置环境变量
3. 或者修改 `config.json` 文件（注意：不要将敏感信息提交到 GitHub）

## 📱 安卓App对接

### 修改 API 地址

在安卓 App 的 `RetrofitClient.kt` 中，将 `BASE_URL` 修改为你的部署地址：

```kotlin
private const val BASE_URL = "https://你的部署地址/"
```

### 测试 API

使用 Postman 或直接在浏览器中访问你的部署地址进行测试。

## ⚠️ 注意事项

1. **免费服务限制**
   - Replit 免费版有休眠机制，一段时间不访问会自动暂停
   - Render 免费版有每月使用时长限制

2. **数据库安全**
   - 不要在代码中硬编码数据库密码
   - 使用环境变量存储敏感信息
   - 配置数据库只允许特定 IP 访问

3. **HTTPS**
   - Replit 和 Render 都默认提供 HTTPS
   - 建议在生产环境始终使用 HTTPS

## 📚 扩展阅读

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Replit 文档](https://docs.replit.com/)
- [Render 文档](https://docs.render.com/)

## 🤝 常见问题

**Q: Replit 上的服务经常打不开怎么办？**
A: 免费版 Replit 会休眠，可以使用 UptimeRobot 等工具定时访问保持活跃。

**Q: 如何添加更多 API 接口？**
A: 直接在 `main.py` 中添加新的路由函数即可，FastAPI 会自动更新文档。

**Q: 可以同时连接多个数据库吗？**
A: 可以，修改 `get_remote_storage()` 函数来支持多个数据源。
