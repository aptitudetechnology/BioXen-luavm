#!/bin/bash

# Test proper XCP-ng XML-RPC authentication
# Based on endpoint testing results, XCP-ng expects XML-RPC on root path

HOST="192.168.1.198:443"
USERNAME="root"
# PASSWORD - you'll need to set this
read -s -p "Enter XCP-ng password: " PASSWORD
echo

echo "🔍 Testing XCP-ng XML-RPC Authentication"
echo "=============================================="
echo "Host: $HOST"
echo "Username: $USERNAME"
echo

# Proper XCP-ng session.login XML-RPC call
XML_REQUEST='<?xml version="1.0"?>
<methodCall>
  <methodName>session.login_with_password</methodName>
  <params>
    <param><value><string>'$USERNAME'</string></value></param>
    <param><value><string>'$PASSWORD'</string></value></param>
  </params>
</methodCall>'

echo "1️⃣  Testing XCP-ng session.login_with_password..."
echo "Sending XML-RPC request..."

RESPONSE=$(curl -k -s \
  -H "Content-Type: text/xml" \
  -X POST \
  -d "$XML_REQUEST" \
  "https://$HOST/")

echo "Response:"
echo "$RESPONSE"
echo

# Check if we got a session ID back
if echo "$RESPONSE" | grep -q "OpaqueRef:"; then
    echo "✅ Authentication successful! Got session reference."
    SESSION_ID=$(echo "$RESPONSE" | grep -o "OpaqueRef:[^<]*")
    echo "Session ID: $SESSION_ID"
    
    echo
    echo "2️⃣  Testing session.get_all_records for VMs..."
    
    # Test getting VM list with the session
    XML_VM_REQUEST='<?xml version="1.0"?>
<methodCall>
  <methodName>VM.get_all_records</methodName>
  <params>
    <param><value><string>'$SESSION_ID'</string></value></param>
  </params>
</methodCall>'
    
    VM_RESPONSE=$(curl -k -s \
      -H "Content-Type: text/xml" \
      -X POST \
      -d "$XML_VM_REQUEST" \
      "https://$HOST/")
    
    echo "VM List Response (first 500 chars):"
    echo "$VM_RESPONSE" | head -c 500
    echo "..."
    
    if echo "$VM_RESPONSE" | grep -q "struct"; then
        echo "✅ VM listing successful! XCP-ng XML-RPC is working."
    else
        echo "❌ VM listing failed."
    fi
    
else
    echo "❌ Authentication failed."
    if echo "$RESPONSE" | grep -q "INVALID_LOGIN"; then
        echo "💡 Invalid username or password"
    elif echo "$RESPONSE" | grep -q "fault"; then
        echo "💡 XML-RPC fault - check format"
    else
        echo "💡 Unexpected response format"
    fi
fi

echo
echo "🏁 XCP-ng XML-RPC testing complete!"
echo "=============================================="
echo "💡 This shows the correct format the library should use:"
echo "   - POST to https://host/ (root path, not /api/session)"
echo "   - Content-Type: text/xml"
echo "   - XML-RPC methodCall format"
echo "   - session.login_with_password for authentication"
