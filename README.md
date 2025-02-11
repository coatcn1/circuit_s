# Circuit 服务端

## 1. 环境要求

- Python 3.8+
- MongoDB 4.4+
- Nginx (用于反向代理)
- Linux 服务器 (推荐 Ubuntu 20.04+)

## 2. 项目结构

```
circuit_s/
├── app/                    # 应用代码
│   ├── api/               # API接口
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── config/                # 配置文件
├── tests/                 # 测试代码
├── scripts/               # 部署脚本
└── requirements.txt       # 项目依赖
```

## 3. 数据库设计

### 3.1 设备表 (devices)

```javascript
{
    "_id": ObjectId,
    "device_id": String,      // 设备唯一标识
    "device_name": String,    // 设备名称
    "device_type": String,    // 设备类型
    "camera_num": Number,     // 摄像头数量
    "ip_address": String,     // IP地址
    "mac_address": String,    // MAC地址
    "token": String,          // 认证令牌
    "status": String,         // 设备状态
    "last_heartbeat": Date,   // 最后心跳��间
    "created_at": Date,       // 创建时间
    "updated_at": Date        // 更新时间
}
```

### 3.2 巡检任务表 (inspections)

```javascript
{
    "_id": ObjectId,
    "inspection_id": String,  // 巡检任务ID
    "device_id": String,      // 设备ID
    "status": String,         // 任务状态
    "start_time": Date,       // 开始时间
    "end_time": Date,         // 结束时间
    "camera_ids": [String],   // 使用的摄像头
    "video_urls": [String],   // 视频文件URL
    "created_at": Date,       // 创建时间
    "updated_at": Date        // 更新时间
}
```

## 4. API 接口

### 4.1 设备管理

- 设备注册
- 设备认证
- 设备状态管理
- WebSocket 连接管理

### 4.2 巡检管理

- 创建巡检任务
- 获取任务状态
- 查看任务历史
- 视频文件管理

### 4.3 系统管理

- 用户认证
- 权限控制
- 系统监控
- 日志管理

## 5. 部署说明

### 5.1 安装依赖

```bash
pip install -r requirements.txt
```

### 5.2 配置文件

创建 `config/config.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  debug: false

database:
  uri: "mongodb://localhost:27017"
  name: "circuit_db"

storage:
  type: "local" # 或 "s3"
  path: "/data/videos" # 本地存储路径

jwt:
  secret_key: "your-secret-key"
  algorithm: "HS256"
  access_token_expire_minutes: 30

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 5.3 Nginx 配置

```nginx
server {
    listen 80;
    server_name circuit.bjzntd.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5.4 运行服务

开发环境：

```bash
uvicorn app.main:app --reload
```

这时候就可以通过 http://localhost:8000/web 访问前端页面

生产环境：

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
