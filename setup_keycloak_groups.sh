#!/bin/bash

# Setup Keycloak groups and add users to groups

KEYCLOAK_URL="http://localhost:8081"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM_NAME="agentgateway"
CLIENT_ID="ext-auth-server"

echo "👥 Setting up Keycloak groups for authorization..."
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

# Create group "test-user"
echo "👥 Creating group: test-user..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/groups" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-user"
  }' > /dev/null

echo "✅ Group 'test-user' created"

# Create group "admin"
echo "👥 Creating group: admin..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/groups" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin"
  }' > /dev/null

echo "✅ Group 'admin' created"

# Get group IDs
GROUP_TEST_USER_ID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/groups" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*","name":"test-user"' | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

GROUP_ADMIN_ID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/groups" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*","name":"admin"' | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

echo "Group test-user ID: ${GROUP_TEST_USER_ID}"
echo "Group admin ID: ${GROUP_ADMIN_ID}"

# Get john.doe user ID
USER_JOHN_ID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users?username=john.doe" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "User john.doe ID: ${USER_JOHN_ID}"

# Add john.doe to test-user group
echo "➕ Adding john.doe to 'test-user' group..."
curl -s -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users/${USER_JOHN_ID}/groups/${GROUP_TEST_USER_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" > /dev/null

echo "✅ john.doe added to 'test-user' group"

# Get client UUID
CLIENT_UUID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients?clientId=${CLIENT_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "Client UUID: ${CLIENT_UUID}"

# Add groups claim to client mapper
echo "🔧 Adding groups mapper to client..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients/${CLIENT_UUID}/protocol-mappers/models" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "groups",
    "protocol": "openid-connect",
    "protocolMapper": "oidc-group-membership-mapper",
    "consentRequired": false,
    "config": {
      "full.path": "false",
      "id.token.claim": "true",
      "access.token.claim": "true",
      "claim.name": "groups",
      "userinfo.token.claim": "true"
    }
  }' > /dev/null

echo "✅ Groups mapper added"

# Create test user without group
echo "👤 Creating user without group: jane.smith..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane.smith",
    "email": "jane@example.com",
    "firstName": "Jane",
    "lastName": "Smith",
    "enabled": true,
    "emailVerified": true
  }' > /dev/null

USER_JANE_ID=$(curl -s -X GET "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users?username=jane.smith" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

curl -s -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users/${USER_JANE_ID}/reset-password" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "password",
    "value": "password123",
    "temporary": false
  }' > /dev/null

echo "✅ User jane.smith created (NO group membership)"

echo ""
echo "✨ Group setup complete!"
echo ""
echo "📋 Summary:"
echo "  Group: test-user"
echo "    - john.doe ✓"
echo "  Group: admin"
echo "    - (empty)"
echo "  No group:"
echo "    - jane.smith"
echo ""
echo "🧪 Test:"
echo "  john.doe (in test-user group) → should be ALLOWED"
echo "  jane.smith (no group) → should be DENIED"
