# 德州扑克游戏后端

这是一个基于 FastAPI 的德州扑克游戏后端服务，提供用户认证、游戏逻辑、实时通信等功能。

## 功能特性

- 🔐 用户注册/登录系统
- 💰 充值和借码功能
- 🎮 完整的德州扑克游戏逻辑
- 🏠 房间管理系统
- 📡 WebSocket 实时通信
- 👨‍💼 后台管理功能
- 📊 数据统计和记录

## 技术栈

- **FastAPI** - 现代化的 Python Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **SQLite** - 轻量级数据库
- **JWT** - 用户认证
- **WebSocket** - 实时通信
- **Pydantic** - 数据验证

## 安装和运行

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python start.py
```

或者直接运行：

```bash
python main.py
```

### 3. 访问服务

- **API 服务**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## API 接口

### 用户认证

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息
- `PUT /api/auth/profile` - 更新用户信息

### 充值和借码

- `POST /api/recharge` - 申请充值
- `POST /api/borrow` - 申请借码
- `GET /api/borrow/history` - 借码历史

### 房间管理

- `GET /api/rooms` - 获取房间列表
- `POST /api/rooms` - 创建房间
- `GET /api/rooms/{room_id}` - 获取房间详情

### 管理员接口

- `GET /api/admin/users` - 获取用户列表
- `POST /api/admin/recharge/approve` - 审批充值
- `POST /api/admin/borrow/approve` - 审批借码
- `PUT /api/admin/config/borrow-amount` - 设置借码数量

## 数据库模型

### 用户表 (User)
- id, username, email, password_hash
- balance (余额), borrow_times (借码次数)
- is_admin, created_at, updated_at

### 房间表 (Room)
- id, name, small_blind, big_blind
- max_players, current_players, status
- created_by, created_at

### 游戏表 (Game)
- id, room_id, players, game_state
- current_pot, community_cards
- created_at, finished_at

### 交易记录表 (Transaction)
- id, user_id, type, amount
- status, created_at, approved_at

### 借码记录表 (BorrowRecord)
- id, user_id, amount, status
- created_at, approved_at

### 系统配置表 (SystemConfig)
- id, key, value, description

## WebSocket 消息格式

### 客户端发送
```json
{
  "type": "join_room",
  "room_id": 1,
  "data": {}
}
```

### 服务器响应
```json
{
  "type": "game_state",
  "data": {
    "room_id": 1,
    "players": [...],
    "pot": 100,
    "community_cards": [...]
  }
}
```

## 环境配置

在 `.env` 文件中配置以下参数：

```env
# 数据库配置
DATABASE_URL=sqlite:///./poker_game.db

# JWT 配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 开发说明

1. **代码结构**：
   - `main.py` - 主应用文件
   - `models.py` - 数据库模型
   - `schemas.py` - Pydantic 模型
   - `auth.py` - 认证相关
   - `game_logic.py` - 游戏逻辑
   - `websocket_handler.py` - WebSocket 处理
   - `database.py` - 数据库配置

2. **数据库迁移**：
   - 首次运行会自动创建数据库表
   - 修改模型后需要重启服务

3. **测试**：
   - 使用 FastAPI 自动生成的文档进行 API 测试
   - WebSocket 可以使用浏览器开发者工具测试

## 注意事项

- 确保前端服务运行在 http://localhost:5173
- 默认管理员账号：admin/admin123
- 借码功能需要管理员审批
- WebSocket 连接需要有效的 JWT token