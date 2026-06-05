# 校食通 — 后端 API

校园点餐系统统一后端服务，为学生端和管理后台提供 RESTful API。

## 技术栈

| 依赖 | 说明 |
|------|------|
| FastAPI | Python Web 框架 |
| Uvicorn | ASGI 服务器 |
| SQLAlchemy | ORM（SQLite） |
| Pydantic | 请求/响应数据校验 |
| python-jose | JWT 令牌签发与验证（HS256） |
| passlib + bcrypt | 密码哈希 |

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv myenv

# 2. 激活虚拟环境（Windows）
myenv\Scripts\activate

# 3. 激活虚拟环境（macOS / Linux）
# source myenv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动开发服务器（默认 http://localhost:8000）
uvicorn app.main:app --reload

# 6. 查看 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
```

首次启动时自动执行：
- 创建数据库表（SQLite）
- 增量迁移补全缺失列（无需删库）
- 填充种子数据（幂等，已有数据则跳过）

## 目录结构

```
backend/
├── requirements.txt
├── campus_ordering.db    # SQLite 数据库文件（自动生成）
├── uploads/              # 上传的图片文件
└── app/
    ├── main.py           # 应用入口：lifespan 事件、CORS、路由注册、静态文件
    ├── api/
    │   ├── deps.py       # FastAPI Depends：get_current_user / get_admin_user
    │   └── v1/endpoints/
    │       ├── auth.py   # 登录/注册/忘记密码/修改密码/充值/地址同步
    │       ├── shops.py  # 商家列表 + 商家详情（含菜品）
    │       ├── orders.py # 创建订单/订单历史/更新状态
    │       ├── admin.py  # 管理端 CRUD（商家/菜品/用户）+ 统计 + 图片上传
    │       └── feedback.py # 学生反馈 + 管理员回复
    ├── models/           # SQLAlchemy ORM 模型
    │   ├── user.py       # 用户表
    │   ├── shop.py       # 商家表
    │   ├── dish.py       # 菜品表（关联 shop）
    │   ├── order.py      # 订单表（关联 user）
    │   └── feedback.py   # 反馈表
    ├── schemas/          # Pydantic 请求/响应 Schema
    ├── services/         # 业务逻辑层
    └── core/
        ├── database.py   # SQLite 引擎 + SessionLocal + get_db 生成器
        ├── security.py   # JWT 生成/解码 + bcrypt 密码哈希/校验
        ├── migrate.py    # 增量数据库迁移（ALTER TABLE 补全列）
        └── seed.py       # 开发种子数据（3 管理员 + 10 商家 + 50+ 菜品 + 40+ 订单）
```

## API 概览

### 统一响应格式

```json
{ "code": 200, "data": <payload>, "msg": "success" }
```

### 公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/register` | 用户注册 |
| POST | `/api/v1/login` | 用户登录，返回 JWT |
| POST | `/api/v1/forgot-password/check` | 忘记密码 — 验证学号 |
| POST | `/api/v1/forgot-password/verify` | 忘记密码 — 验证密保 |
| POST | `/api/v1/forgot-password/reset` | 忘记密码 — 重置密码 |
| GET | `/api/v1/shops` | 商家列表 |
| GET | `/api/v1/shops/{id}` | 商家详情（含菜品） |

### 学生端（需 Bearer Token）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/users/me` | 获取当前用户信息 |
| PUT | `/api/v1/users/me/password` | 修改密码 |
| PUT | `/api/v1/users/me/topup` | 钱包充值 |
| PUT | `/api/v1/users/me/addresses` | 同步收货地址 |
| POST | `/api/v1/logout` | 退出登录 |
| POST | `/api/v1/orders` | 创建订单 |
| GET | `/api/v1/orders` | 订单历史 |
| PUT | `/api/v1/orders/{id}/status` | 更新订单状态 |
| POST | `/api/v1/feedback` | 提交反馈 |
| GET | `/api/v1/feedback/my` | 我的反馈 |
| GET | `/api/v1/feedback/unread-count` | 未读回复数 |
| PATCH | `/api/v1/feedback/{id}/read` | 标记已读 |
| PATCH | `/api/v1/feedback/read-all` | 全部已读 |
| DELETE | `/api/v1/feedback/{id}` | 删除反馈 |
| DELETE | `/api/v1/feedback/clear-all` | 清空反馈 |

### 管理端（需 Admin 权限）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/stats` | 仪表盘统计（支持 `?date=` 筛选） |
| POST | `/api/v1/admin/upload` | 图片上传 |
| GET/POST/PUT/DELETE | `/api/v1/admin/shops` | 商家 CRUD |
| GET/POST/PUT/DELETE | `/api/v1/admin/dishes` | 菜品 CRUD |
| GET/POST/PUT/DELETE | `/api/v1/admin/users` | 用户 CRUD |
| GET | `/api/v1/admin/orders` | 全部订单列表 |
| GET/PUT/DELETE | `/api/v1/admin/feedback` | 反馈/留言管理 |

## 数据库

SQLite 单文件 `campus_ordering.db`，5 张表：

| 表 | 主要字段 |
|----|---------|
| `users` | student_id (PK), name, password_hash, balance, avatar, addresses (JSON), security_question/answer |
| `shops` | id (PK), name, rating, sales, image, tags (JSON), discount, bulletin |
| `dishes` | id (PK), name, price, image, category, sales, shop_id (FK) |
| `orders` | id (PK), student_id (FK), shop_name, items (JSON), total_price, status, dining_type, pickup_time |
| `feedbacks` | id (PK), student_id, type, category, content, reply, status, student_read, student_deleted |

种子数据预置账号：

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | 123456 |
| 学生 | 123456 | 123456 |
| 学生 | 2023110402 | 123456 |

## 认证机制

- **JWT HS256**，过期时间 24 小时
- 登录签发，客户端通过 `Authorization: Bearer <token>` 携带
- `get_current_user` 依赖注入自动解码并查询用户
- `get_admin_user` 在前者基础上额外检查 `student_id === "admin"`

## CORS 配置

默认允许以下来源：
- `http://localhost:3000`（学生端 Next.js）
- `http://localhost:5173`（管理后台 Vite）
