# Dockerfile cho agentgateway trên AlmaLinux (Red Hat compatible) với AMD64
FROM almalinux:9

# Cài đặt dependencies cần thiết
RUN dnf update -y && \
    dnf install -y --allowerasing wget tar gzip curl && \
    dnf clean all

# Cài đặt Node.js 20 từ NodeSource repository và socat
RUN curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && \
    dnf install -y nodejs socat

# Cài đặt Python và uv/uvx  
RUN dnf install -y python3 python3-pip && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv && \
    cp /root/.local/bin/uvx /usr/local/bin/uvx && \
    chmod +x /usr/local/bin/uv /usr/local/bin/uvx

# Kiểm tra npm, npx và uvx
RUN node --version && npm --version && npx --version && uvx --version

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt agentgateway binary (latest version)
RUN curl -s https://api.github.com/repos/agentgateway/agentgateway/releases/latest | \
    grep "browser_download_url.*linux-amd64" | \
    cut -d '"' -f 4 | \
    xargs curl -L -o agentgateway-linux-amd64 && \
    chmod +x agentgateway-linux-amd64 && \
    mv agentgateway-linux-amd64 /usr/local/bin/agentgateway

# Copy config file
COPY config.yaml /app/config.yaml

# Copy start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set environment variables for binding
ENV AGENTGATEWAY_ADMIN_HOST=0.0.0.0
ENV AGENTGATEWAY_ADMIN_PORT=15000

# Expose ports
EXPOSE 3000 15000

# Chạy agentgateway
CMD ["/app/start.sh"]