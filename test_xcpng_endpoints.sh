#!/bin/bash

# XCP-ng API Endpoint Testing Script
# This script tests various XCP-ng API endpoints to find the correct one

HOST="192.168.1.198:443"
USERNAME="root"

echo "🔍 Testing XCP-ng API Endpoints for: $HOST"
echo "=============================================="

# Test 1: Basic connectivity
echo -e "\n1️⃣  Testing basic HTTPS connectivity..."
curl -k -v --connect-timeout 10 "https://$HOST/" 2>&1 | head -20

# Test 2: Check what the library is trying to use
echo -e "\n2️⃣  Testing /api/session endpoint (what library tries)..."
curl -k -v --connect-timeout 10 "https://$HOST/api/session" 2>&1 | head -10

# Test 3: Common XCP-ng/XenServer endpoints
echo -e "\n3️⃣  Testing /jsonrpc endpoint..."
curl -k -v --connect-timeout 10 "https://$HOST/jsonrpc" 2>&1 | head -10

echo -e "\n4️⃣  Testing root path /..."
curl -k -v --connect-timeout 10 "https://$HOST/" 2>&1 | head -10

echo -e "\n5️⃣  Testing /session endpoint..."
curl -k -v --connect-timeout 10 "https://$HOST/session" 2>&1 | head -10

# Test 6: XML-RPC endpoint (traditional XenServer)
echo -e "\n6️⃣  Testing XML-RPC endpoint..."
curl -k -v --connect-timeout 10 -H "Content-Type: text/xml" "https://$HOST/" 2>&1 | head -10

# Test 7: Options request to see what methods are available
echo -e "\n7️⃣  Testing OPTIONS request..."
curl -k -v --connect-timeout 10 -X OPTIONS "https://$HOST/" 2>&1 | head -15

echo -e "\n🏁 Endpoint testing complete!"
echo "=============================================="
echo "💡 Look for responses that don't return HTTP 500 errors"
echo "💡 The correct endpoint should return XML or JSON, not HTML error pages"
