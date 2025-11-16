@echo off
echo ===============================================
echo 🚀 AgentGateway Docker Setup for Windows
echo ===============================================
echo.

REM Kiểm tra Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker không được tìm thấy. Vui lòng cài đặt Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker đã được tìm thấy

REM Kiểm tra Docker Compose  
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose không được tìm thấy.
    pause
    exit /b 1
)

echo ✅ Docker Compose đã được tìm thấy
echo.

echo 🔄 Đang build Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Build thất bại
    pause
    exit /b 1
)

echo ✅ Build thành công
echo.

echo 🚀 Đang khởi động AgentGateway container...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Khởi động thất bại
    pause
    exit /b 1
)

echo.
echo ===============================================  
echo 🎉 AgentGateway đã khởi động thành công!
echo ===============================================
echo.
echo 📊 Web UI: http://localhost:15000/ui
echo 🔗 API Gateway: http://localhost:3000
echo.
echo 📝 Để xem logs: docker-compose logs -f agentgateway
echo 🛑 Để dừng: docker-compose down
echo.

REM Mở browser
echo 🌐 Đang mở Web UI...
timeout /t 3 /nobreak >nul
start http://localhost:15000/ui

echo.
echo ✨ Setup hoàn tất! 
pause