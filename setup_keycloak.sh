#!/bin/bash

# Setup Keycloak realm and users for JWT authentication testing

KEYCLOAK_URL="http://localhost:8081"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM_NAME="agentgateway"
CLIENT_ID="ext-auth-server"

echo "🔐 Setting up Keycloak for AgentGateway JWT authentication..."
echo ""

# Wait for Keycloak to be ready
echo "⏳ Waiting for Keycloak to be ready..."
sleep 5

# Get admin token
echo "📝 Getting admin access token..."
ADMIN_TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASSWORD}" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ Failed to get admin token"
  exit 1
fi

echo "✅ Got admin token"

# Create realm
echo "🌍 Creating realm: ${REALM_NAME}..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"realm\": \"${REALM_NAME}\",
    \"enabled\": true
  }" > /dev/null

echo "✅ Realm created"

# Create client
echo "🔧 Creating client: ${CLIENT_ID}..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"clientId\": \"${CLIENT_ID}\",
    \"enabled\": true,
    \"publicClient\": false,
    \"directAccessGrantsEnabled\": true,
    \"standardFlowEnabled\": true,
    \"implicitFlowEnabled\": false,
    \"serviceAccountsEnabled\": false,
    \"redirectUris\": [\"*\"],
    \"webOrigins\": [\"*\"]
  }" > /dev/null

echo "✅ Client created"

# Get client secret
CLIENT_UUID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients?clientId=${CLIENT_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

CLIENT_SECRET=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients/${CLIENT_UUID}/client-secret" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"value":"[^"]*"' | cut -d'"' -f4)

echo "🔑 Client Secret: ${CLIENT_SECRET}"

# Create user john.doe
echo "👤 Creating user: john.doe..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe",
    "email": "john@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "enabled": true,
    "emailVerified": true,
    "attributes": {
      "keycloak_id": ["test-user-1"]
    }
  }' > /dev/null

# Get user ID and set password
USER_ID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users?username=john.doe" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

curl -s -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users/${USER_ID}/reset-password" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "password",
    "value": "password123",
    "temporary": false
  }' > /dev/null

echo "✅ User john.doe created with password: password123"

echo ""
echo "✨ Keycloak setup complete!"
echo ""
echo "📋 Configuration Summary:"
echo "  Realm: ${REALM_NAME}"
echo "  Client ID: ${CLIENT_ID}"
echo "  Client Secret: ${CLIENT_SECRET}"
echo "  User: john.doe / password123"
echo ""
echo "🧪 Test getting a token:"
echo "curl -X POST ${KEYCLOAK_URL}/realms/${REALM_NAME}/protocol/openid-connect/token \\"
echo "  -d 'client_id=${CLIENT_ID}' \\"
echo "  -d 'client_secret=${CLIENT_SECRET}' \\"
echo "  -d 'username=john.doe' \\"
echo "  -d 'password=password123' \\"
echo "  -d 'grant_type=password'"
