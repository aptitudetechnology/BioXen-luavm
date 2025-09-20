#!/bin/bash

# Quick XCP-ng XML-RPC Authentication Test
# Run this to test if XCP-ng credentials work with proper XML-RPC format

HOST="192.168.1.198:443"
echo "🔍 Quick XCP-ng Authentication Test"
echo "=================================="
echo "Host: $HOST"
echo

# Get password securely
read -s -p "Enter XCP-ng root password: " PASSWORD
echo
echo

# Simple session.login_with_password test
echo "Testing session.login_with_password..."

XML_REQUEST='<?xml version="1.0"?>
<methodCall>
  <methodName>session.login_with_password</methodName>
  <params>
    <param><value><string>root</string></value></param>
    <param><value><string>'$PASSWORD'</string></value></param>
  </params>
</methodCall>'

RESPONSE=$(curl -k -s -w "\nHTTP_STATUS:%{http_code}\n" \
  -H "Content-Type: text/xml" \
  -X POST \
  -d "$XML_REQUEST" \
  "https://$HOST/")

echo "Response:"
echo "$RESPONSE"
echo

# Check results
if echo "$RESPONSE" | grep -q "HTTP_STATUS:200"; then
    echo "✅ HTTP 200 - Server responded"
    if echo "$RESPONSE" | grep -q "OpaqueRef:"; then
        echo "✅ Authentication SUCCESS - Got session reference!"
        echo "💡 XCP-ng credentials work with proper XML-RPC format"
    elif echo "$RESPONSE" | grep -q "INVALID_LOGIN"; then
        echo "❌ Authentication FAILED - Invalid credentials"
    else
        echo "⚠️  Unexpected response format"
    fi
else
    echo "❌ HTTP error or connection failed"
fi

echo
echo "🏁 Test complete!"
echo "💡 This shows the correct format that the library should use"
