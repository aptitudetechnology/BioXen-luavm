#!/bin/bash

# XCP-ng API Response Testing Script
# This script tests XCP-ng endpoints and shows the actual HTTP responses

HOST="192.168.1.198:443"

echo "🔍 Testing XCP-ng API Response Content for: $HOST"
echo "=============================================="

# Test 1: What the library tries - /api/session
echo -e "\n1️⃣  Testing /api/session endpoint (what the library uses)..."
echo "Response:"
curl -k -s --max-time 10 "https://$HOST/api/session" | head -5
echo -e "\nHTTP Status:"
curl -k -s -o /dev/null -w "%{http_code}" "https://$HOST/api/session"
echo ""

# Test 2: Root path
echo -e "\n2️⃣  Testing root path /..."
echo "Response:"
curl -k -s --max-time 10 "https://$HOST/" | head -5
echo -e "\nHTTP Status:"
curl -k -s -o /dev/null -w "%{http_code}" "https://$HOST/"
echo ""

# Test 3: JSON-RPC endpoint (common for XCP-ng)
echo -e "\n3️⃣  Testing /jsonrpc endpoint..."
echo "Response:"
curl -k -s --max-time 10 "https://$HOST/jsonrpc" | head -5
echo -e "\nHTTP Status:"
curl -k -s -o /dev/null -w "%{http_code}" "https://$HOST/jsonrpc"
echo ""

# Test 4: Session endpoint without /api
echo -e "\n4️⃣  Testing /session endpoint..."
echo "Response:"
curl -k -s --max-time 10 "https://$HOST/session" | head -5
echo -e "\nHTTP Status:"
curl -k -s -o /dev/null -w "%{http_code}" "https://$HOST/session"
echo ""

# Test 5: Try a POST to the root with XML-RPC format
echo -e "\n5️⃣  Testing XML-RPC POST to root..."
echo "Response:"
curl -k -s --max-time 10 -X POST -H "Content-Type: text/xml" -d '<?xml version="1.0"?><methodCall><methodName>session.login_with_password</methodName></methodCall>' "https://$HOST/" | head -5
echo -e "\nHTTP Status:"
curl -k -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: text/xml" -d '<?xml version="1.0"?><methodCall><methodName>session.login_with_password</methodName></methodCall>' "https://$HOST/"
echo ""

# Test 6: Check if it's really XCP-ng by looking for specific headers
echo -e "\n6️⃣  Testing for XCP-ng specific headers..."
echo "Headers from root:"
curl -k -s -I --max-time 10 "https://$HOST/" | grep -i "server\|xapi\|xen\|citrix"

echo -e "\n🏁 Response testing complete!"
echo "=============================================="
echo "💡 Look for endpoints that return XML or JSON instead of HTML"
echo "💡 HTTP 200 responses are good, 404/500 are bad"
echo "💡 XCP-ng typically uses XML-RPC on the root path"
