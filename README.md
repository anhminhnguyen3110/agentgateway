# AgentGateway Docker Setup

Đây là setup Docker cho AgentGateway trên môi trường Red Hat Linux với architecture AMD64.

## Prerequisites

- Docker Desktop đã được cài đặt trên Windows
- Docker Compose

## Cách sử dụng

### 1. Build và chạy container

```powershell
# Build Docker image
docker-compose build

# Chạy container
docker-compose up -d

# Hoặc chạy trong foreground để xem logs
docker-compose up
```

### 2. Truy cập AgentGateway

- **UI Interface**: http://localhost:15000/ui
- **Gateway API**: http://localhost:3000

### 3. Kiểm tra logs

```powershell
docker-compose logs -f agentgateway
```

### 4. Dừng container

```powershell
docker-compose down
```

## Cấu trúc

- `Dockerfile`: Định nghĩa môi trường Red Hat Linux với agentgateway và npx
- `docker-compose.yml`: Orchestration file để chạy container
- Port mapping:
  - 3000: Gateway API port
  - 15000: Web UI port

## Features

- ✅ Red Hat Linux base image
- ✅ AMD64 architecture
- ✅ Node.js và npx đã được cài sẵn
- ✅ AgentGateway binary latest version
- ✅ Default configuration từ repository chính thức
- ✅ Health check được cấu hình
- ✅ Auto-restart container

## Configuration

File config mặc định sẽ được tải tự động từ repository chính thức. Bạn có thể tùy chỉnh bằng cách:

1. Tạo thư mục `config` trong thư mục hiện tại
2. Đặt file `config.yaml` tùy chỉnh vào đó
3. Restart container

## Troubleshooting

### Kiểm tra container đang chạy:
```powershell
docker ps
```

### Kiểm tra logs:
```powershell
docker-compose logs agentgateway
```

### Vào shell của container:
```powershell
docker-compose exec agentgateway /bin/bash
```