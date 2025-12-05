#!/bin/bash
# ============================================
# KONG API GATEWAY SECURITY CONFIGURATION
# For LLM Inference Endpoints
# ============================================

KONG_ADMIN="http://localhost:10001"

echo "════════════════════════════════════════════"
echo "  CONFIGURING KONG API GATEWAY FOR LLM"
echo "════════════════════════════════════════════"
echo ""

# Wait for Kong to be ready
echo "⏳ Waiting for Kong to be ready..."
until curl -s $KONG_ADMIN/status > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Kong is ready!"
echo ""

# ============================================
# STEP 1: Create LLM Inference Service
# ============================================
echo "📦 Creating LLM Inference Service..."
curl -s -X POST $KONG_ADMIN/services \
  --data "name=llm-inference" \
  --data "url=http://ollama:11434" \
  | jq '.'

echo ""

# ============================================
# STEP 2: Create Route for LLM API
# ============================================
echo "🛤️  Creating Route..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/routes \
  --data "name=llm-route" \
  --data "paths[]=/api/llm" \
  --data "strip_path=true" \
  | jq '.'

echo ""

# ============================================
# STEP 3: Add Key Authentication Plugin
# ============================================
echo "🔐 Adding API Key Authentication..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/plugins \
  --data "name=key-auth" \
  --data "config.key_names=X-API-Key" \
  --data "config.hide_credentials=true" \
  | jq '.'

echo ""

# ============================================
# STEP 4: Add Rate Limiting Plugin
# ============================================
echo "⏱️  Adding Rate Limiting..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100" \
  --data "config.hour=1000" \
  --data "config.policy=redis" \
  --data "config.redis_host=redis" \
  --data "config.redis_port=6379" \
  | jq '.'

echo ""

# ============================================
# STEP 5: Add Request Size Limiting
# ============================================
echo "📏 Adding Request Size Limit..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/plugins \
  --data "name=request-size-limiting" \
  --data "config.allowed_payload_size=10" \
  | jq '.'

echo ""

# ============================================
# STEP 6: Add IP Restriction (Optional)
# ============================================
echo "🌐 Adding IP Restriction (demo mode - all allowed)..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/plugins \
  --data "name=ip-restriction" \
  --data "config.allow=0.0.0.0/0" \
  | jq '.'

echo ""

# ============================================
# STEP 7: Add Request/Response Logging
# ============================================
echo "📝 Adding Request Logging..."
curl -s -X POST $KONG_ADMIN/services/llm-inference/plugins \
  --data "name=file-log" \
  --data "config.path=/tmp/llm-access.log" \
  | jq '.'

echo ""

# ============================================
# STEP 8: Create Consumer (API User)
# ============================================
echo "👤 Creating API Consumer..."
curl -s -X POST $KONG_ADMIN/consumers \
  --data "username=llm-app-user" \
  --data "custom_id=app-001" \
  | jq '.'

echo ""

# ============================================
# STEP 9: Create API Key for Consumer
# ============================================
echo "🔑 Generating API Key..."
API_KEY_RESPONSE=$(curl -s -X POST $KONG_ADMIN/consumers/llm-app-user/key-auth \
  --data "key=demo-api-key-12345")

API_KEY=$(echo $API_KEY_RESPONSE | jq -r '.key')
echo "API Key: $API_KEY"
echo ""

# ============================================
# STEP 10: Create Premium Consumer with Higher Limits
# ============================================
echo "👤 Creating Premium Consumer..."
curl -s -X POST $KONG_ADMIN/consumers \
  --data "username=llm-premium-user" \
  --data "custom_id=premium-001" \
  | jq '.'

# Create API key for premium user
curl -s -X POST $KONG_ADMIN/consumers/llm-premium-user/key-auth \
  --data "key=premium-api-key-99999" \
  | jq '.'

# Add higher rate limit for premium consumer
curl -s -X POST $KONG_ADMIN/consumers/llm-premium-user/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=1000" \
  --data "config.hour=10000" \
  --data "config.policy=redis" \
  --data "config.redis_host=redis" \
  --data "config.redis_port=6379" \
  | jq '.'
echo ""

# ============================================
# SUMMARY
# ============================================
echo "════════════════════════════════════════════"
echo "  CONFIGURATION COMPLETE! ✅"
echo "════════════════════════════════════════════"
echo ""
echo "Endpoints:"
echo "  • LLM API:      http://localhost:10000/api/llm"
echo "  • Kong Admin:   http://localhost:10001"
echo "  • Kong GUI:     http://localhost:10002"
echo ""
echo "API Keys:"
echo "  • Standard:  demo-api-key-12345  (100 req/min)"
echo "  • Premium:   premium-api-key-99999  (1000 req/min)"
echo ""
echo "Security Features Enabled:"
echo "  ✅ API Key Authentication"
echo "  ✅ Rate Limiting (Redis-backed)"
echo "  ✅ Request Size Limiting (10MB max)"
echo "  ✅ IP Restriction (configurable)"
echo "  ✅ Request Logging"
echo ""
