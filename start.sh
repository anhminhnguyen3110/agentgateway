#!/bin/bash

# Script khởi động AgentGateway trong container
echo "==============================================="
echo "🚀 Starting AgentGateway..."
echo "==============================================="
echo ""
echo "📊 UI Interface: http://localhost:15000/ui"  
echo "🔗 Gateway API: http://localhost:3000"
echo ""
echo "⏳ Khởi động AgentGateway với config mặc định..."
echo ""

# Kiểm tra xem npx có hoạt động không
if command -v npx &> /dev/null; then
    echo "✅ NPX đã được cài đặt"
    npx --version
else
    echo "❌ NPX không được tìm thấy"
    exit 1
fi

# Kiểm tra agentgateway binary
if command -v agentgateway &> /dev/null; then
    echo "✅ AgentGateway binary đã sẵn sàng"
    agentgateway --version 2>/dev/null || echo "Version check failed, but binary exists"
else
    echo "❌ AgentGateway binary không được tìm thấy"
    exit 1
fi

# Kiểm tra config file  
if [ -f /app/config.yaml ]; then
    echo "✅ Config file found (mounted)"
    echo "📄 Config preview:"
    head -5 /app/config.yaml
    CONFIG_FILE="/app/config.yaml"
elif [ -f /app/config-basic.yaml ]; then
    echo "✅ Basic config file found (built-in)" 
    echo "📄 Config preview:"
    head -5 /app/config-basic.yaml
    CONFIG_FILE="/app/config-basic.yaml"
else
    echo "❌ No config file found"
    exit 1
fi

echo ""
echo "🔄 Đang khởi động AgentGateway..."
echo "🔗 Setting up port forwarding cho Admin UI accessibility"

# Start server-everything in SSE mode first  
echo "🔧 Starting server-everything in SSE mode on port 3001..."
npx @modelcontextprotocol/server-everything sse --port 3001 &
SERVER_EVERYTHING_PID=$!
sleep 3  # Wait for server to start

# Start agentgateway in background
agentgateway -f "$CONFIG_FILE" &
AGENTGATEWAY_PID=$!

# Đợi agentgateway start
sleep 3

# Setup port forwarding để external access có thể kết nối
echo "🌐 Setting up socat forwarding: 0.0.0.0:15000 -> 127.0.0.1:15000"
socat TCP4-LISTEN:15001,bind=0.0.0.0,fork TCP4:127.0.0.1:15000 &

# Keep script running
wait $AGENTGATEWAY_PID