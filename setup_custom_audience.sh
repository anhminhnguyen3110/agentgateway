#!/bin/bash

# Add custom audience mapper to Keycloak client

KEYCLOAK_URL="http://localhost:8081"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM_NAME="agentgateway"
CLIENT_ID="ext-auth-server"

echo "🔧 Adding custom audience to Keycloak client..."
echo ""

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

# Get client UUID
CLIENT_UUID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients?clientId=${CLIENT_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Client UUID: ${CLIENT_UUID}"

# Add audience mapper
echo "🎯 Adding audience mapper for 'agentgateway-api'..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients/${CLIENT_UUID}/protocol-mappers/models" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "agentgateway-audience",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-audience-mapper",
    "consentRequired": false,
    "config": {
      "included.client.audience": "agentgateway-api",
      "id.token.claim": "true",
      "access.token.claim": "true"
    }
  }' > /dev/null

echo "✅ Audience mapper added"

echo ""
echo "✨ Custom audience setup complete!"
echo ""
echo "📋 Token will now include:"
echo '  "aud": ["account", "agentgateway-api"]'
echo ""
echo "🧪 Test getting a new token:"
echo "curl -X POST ${KEYCLOAK_URL}/realms/${REALM_NAME}/protocol/openid-connect/token \\"
echo "  -d 'client_id=${CLIENT_ID}' \\"
echo "  -d 'client_secret=CBOXD8o118VHRYKRTEa8pTyLO3jSK9ew' \\"
echo "  -d 'username=john.doe' \\"
echo "  -d 'password=password123' \\"
echo "  -d 'grant_type=password'"
