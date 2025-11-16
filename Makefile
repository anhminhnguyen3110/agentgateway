# AgentGateway Docker Environment

# Container logs
logs:
	docker-compose logs -f agentgateway

# Build và start
build:
	docker-compose build

up:
	docker-compose up -d

# Build và start combined  
start: build up
	@echo "🎉 AgentGateway started!"
	@echo "📊 UI: http://localhost:15000/ui"
	@echo "🔗 API: http://localhost:3000"

# Stop containers
down:
	docker-compose down

# Restart
restart: down start

# Clean up
clean:
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# Shell vào container
shell:
	docker-compose exec agentgateway /bin/bash

# Status check
status:
	docker-compose ps

# View config
config:
	docker-compose exec agentgateway cat /app/config.yaml

# Health check
health:
	@echo "Checking AgentGateway health..."
	@curl -s http://localhost:15000/ui > /dev/null && echo "✅ UI accessible" || echo "❌ UI not accessible"
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Gateway accessible" || echo "❌ Gateway not accessible"

.PHONY: logs build up start down restart clean shell status config health