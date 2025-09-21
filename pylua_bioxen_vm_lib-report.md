# pylua_bioxen_vm_lib XCP-ng Integration Issue Report

**Date:** September 20, 2025  
**Library Version:** 0.1.22  
**Reporter:** BioXen-luavm Project Team  
**Environment:** Production XCP-ng deployment  

## Executive Summary

The `pylua_bioxen_vm_lib` library version 0.1.22 has a critical compatibility issue with XCP-ng hypervisor integration. While all core VM functionality works perfectly (100% test pass rate for basic VMs), XCP-ng VM creation fails due to an API protocol mismatch. The library attempts to use REST API endpoints that don't exist on XCP-ng, which exclusively uses XML-RPC protocol.

## Issue Classification

- **Severity:** High (blocks XCP-ng VM creation entirely)
- **Impact:** Complete failure of XCP-ng integration feature
- **Scope:** XCP-ng VM type only (basic VMs unaffected)
- **Root Cause:** API protocol incompatibility

## Technical Analysis

### Working Components ✅

1. **Basic VM Creation**: 100% functional
   - Subprocess-based VMs work perfectly
   - All library tests pass (6/6 success rate)
   - Package installation, session management, async execution all working

2. **Core Library Functions**: Fully operational
   - `create_vm()` factory function
   - `VMManager` context management
   - `Curator` system health checks
   - `EnvironmentManager` validation

### Failing Component ❌

**XCP-ng VM Creation**: Complete failure

**Error Pattern:**
```
Authentication failed: 500 - HTTP 500 internal server error
XML parsing error: close_tag/open_tag mismatch
```

### Root Cause Analysis

#### Current Library Behavior
```python
# Library attempts REST API call
URL: https://{hostname}/api/session
Method: POST
Content-Type: application/json
Body: {"username": "root", "password": "***"}
```

#### XCP-ng Expected Behavior
```xml
<!-- XCP-ng expects XML-RPC -->
URL: https://{hostname}/
Method: POST
Content-Type: text/xml
Body: 
<?xml version="1.0"?>
<methodCall>
  <methodName>session.login_with_password</methodName>
  <params>
    <param><value><string>root</string></value></param>
    <param><value><string>***</string></value></param>
  </params>
</methodCall>
```

## API Endpoint Testing Results

Comprehensive endpoint testing was performed on XCP-ng host `192.168.1.198:443`:

| Endpoint | HTTP Status | Response Type | Library Usage |
|----------|-------------|---------------|---------------|
| `/api/session` | 404 | HTML Error | ❌ Library tries this |
| `/` | 200 | HTML/XML-RPC | ✅ XCP-ng accepts this |
| `/jsonrpc` | 404 | HTML Error | ❌ Not available |
| `/session` | 404 | HTML Error | ❌ Not available |

**XML-RPC Test Results:**
- Proper XML-RPC calls to root path (`/`) work correctly
- Authentication with `session.login_with_password` succeeds
- VM operations via XML-RPC are functional

### XCP-ng Configuration Analysis

**Question: Is this a configuration issue rather than a protocol mismatch?**

**Evidence suggesting this is NOT a configuration issue:**

1. **XCP-ng Server is Responding Correctly:**
   - Root path (`/`) returns HTTP 200 ✅
   - Server identifies as "Xapi Server" in error messages ✅
   - HTTPS/SSL handshake completes successfully ✅
   - XML-RPC endpoint is accessible and functional ✅

2. **Standard XCP-ng Behavior:**
   - XCP-ng/Citrix Hypervisor has NEVER used `/api/session` endpoints
   - The Xen API (XAPI) is exclusively XML-RPC based by design
   - `/api/session` is a modern REST API pattern not used by XCP-ng
   - All XCP-ng documentation shows XML-RPC examples on root path

3. **Server Response Analysis:**
   ```html
   <hr><address>Xapi Server</address>
   ```
   This confirms the server is running XAPI (Xen API) which is XML-RPC only.

**What would indicate a configuration issue:**
- ❌ No response from server (connection refused)
- ❌ SSL/TLS errors
- ❌ Authentication failures with correct XML-RPC format
- ❌ XML-RPC returning HTTP 500 for valid calls

**What we actually see (indicating correct configuration):**
- ✅ Server responds to all requests
- ✅ Proper error messages for non-existent endpoints
- ✅ HTTP 200 for root path
- ✅ XML-RPC parser errors only when library sends wrong format

**Conclusion:** The XCP-ng server is properly configured and functioning normally. The issue is that the library expects a REST API that XCP-ng simply doesn't provide by design.

## Detailed Error Trace

```
🐛 DEBUG: Library will attempt to connect to:
  Full URL: https://192.168.1.198:443/api/session
  Host: 192.168.1.198:443
  Username: root

❌ Failed to create XCP-ng VM: Authentication failed: 500 - HTTP 500 internal server error
🐛 DEBUG: Exception type: <class name>
🐛 DEBUG: Exception details: XML parsing error
```

**HTTP Response from XCP-ng:**
```html
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head><title>404 Not Found</title></head>
<body>
<h1>Not Found</h1>
<p>The requested URL /api/session was not found on this server.</p>
<hr><address>Xapi Server</address></body>
</html>
```

## Proposed Solution

### Required Changes

1. **Protocol Migration**: REST API → XML-RPC
   ```python
   # Current (broken)
   requests.post(f"https://{host}/api/session", json=credentials)
   
   # Required (working)
   xml_request = create_xmlrpc_call("session.login_with_password", [username, password])
   requests.post(f"https://{host}/", data=xml_request, headers={"Content-Type": "text/xml"})
   ```

2. **Endpoint Correction**: `/api/session` → `/`
   - Remove REST API assumptions
   - Use XCP-ng root path for all operations

3. **Response Parsing**: JSON → XML-RPC
   ```python
   # Parse XML-RPC responses instead of JSON
   session_ref = parse_xmlrpc_response(response.text)
   ```

4. **Authentication Method**: Update to use proper XCP-ng XML-RPC methods
   - `session.login_with_password` for authentication
   - `VM.get_all_records` for VM listing
   - `VM.create` for VM creation

### Backward Compatibility

The changes should maintain compatibility with existing basic VM functionality while adding proper XCP-ng support:

```python
def create_vm(vm_id, vm_type="basic", config=None):
    if vm_type == "xcpng":
        return XCPngVM(vm_id, config)  # Use XML-RPC protocol
    else:
        return BasicVM(vm_id, config)  # Keep existing subprocess implementation
```

## Testing Evidence

### Successful XML-RPC Test
Manual XML-RPC authentication test confirms XCP-ng connectivity:
```bash
curl -k -H "Content-Type: text/xml" -X POST \
  -d '<?xml version="1.0"?><methodCall>...</methodCall>' \
  https://192.168.1.198:443/
# Returns: HTTP 200 with session reference
```

### Library Test Results
```
📊 TEST RESULTS SUMMARY
✅ Passed: 6
❌ Failed: 0  
📈 Success Rate: 100.0%

1️⃣ Basic VM creation: PASSED
2️⃣ Networked VM creation: PASSED  
3️⃣ VM Manager context: PASSED
4️⃣ Async execution: PASSED
5️⃣ Curator health check: PASSED
6️⃣ Environment validation: PASSED
```

## Environment Details

- **XCP-ng Version:** Latest (XML-RPC enabled)
- **Python Version:** 3.x
- **Library Version:** pylua-bioxen-vm-lib==0.1.22
- **Network:** HTTPS (port 443)
- **Authentication:** Username/password (root)

## Workaround

Until the library is fixed, users can:
1. Use basic VMs for all Lua development (100% functional)
2. Manually manage XCP-ng VMs via XML-RPC if needed
3. Run library tests to verify core functionality

## Recommended Priority

**HIGH PRIORITY** - This blocks a major advertised feature of the library. XCP-ng integration is essential for production hypervisor deployments.

## Implementation Suggestions

1. **Add XML-RPC Client**: Use `xmlrpc.client` or similar
2. **Create XCP-ng Session Manager**: Handle XML-RPC session lifecycle
3. **Update VM Factory**: Add XCP-ng VM class with proper XML-RPC calls
4. **Add Integration Tests**: Test against real XCP-ng instances
5. **Documentation Update**: Reflect XML-RPC requirements

## Contact Information

For additional details or testing access:
- **Project:** BioXen-luavm
- **Repository:** https://github.com/aptitudetechnology/BioXen-luavm
- **Test Environment:** Available for library maintainer testing

## Appendix: Technical Verification

### XCP-ng XML-RPC Documentation References
- XCP-ng uses Xen API (XAPI) which is XML-RPC based
- Standard endpoint: `https://host/` (root path)
- Authentication: `session.login_with_password`
- All operations use XML-RPC methodology

### Library Code Locations Requiring Updates
Based on error traces, the following areas need modification:
- XCP-ng VM creation logic
- Authentication handling
- API endpoint configuration
- Response parsing mechanisms

---

**Status:** Ready for implementation  
**Next Steps:** Library maintainer to implement XML-RPC support for XCP-ng integration
