#!/usr/bin/env python3
"""
Direct XCP-ng API Testing Script
Tests XCP-ng VM creation without interactive menus.
"""

import sys
import traceback
from pylua_bioxen_vm_lib import create_vm

def test_xcpng_vm_creation():
    """Test XCP-ng VM creation with proper debugging"""
    print("🧪 Testing XCP-ng VM Creation (Non-Interactive)")
    print("=" * 60)
    
    # Configuration matching what we know works from the interactive script
    config = {
        "xapi_url": "192.168.1.198:443",  # Hostname:port format (no https://)
        "username": "root", 
        "password": "your_password_here",  # You'll need to update this
        "template_name": "lua-bio-template",
        "vm_name_prefix": "bioxen-lua",
        "ssh_user": "root",
        "ssh_key_path": "",
        
        # Add compatibility fields that the library might expect
        "xcp_host": "192.168.1.198:443",
        "xcp_username": "root",
        "xcp_password": "your_password_here",  # You'll need to update this
        "vm_username": "root",
        "vm_password": "your_password_here"   # You'll need to update this
    }
    
    print("🔧 Configuration:")
    for key, value in config.items():
        if 'password' in key.lower():
            print(f"  {key}: *** (hidden)")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🌐 Testing connection to: https://{config['xapi_url']}")
    print("🔄 Creating XCP-ng VM...")
    
    try:
        # Attempt to create the VM
        vm_instance = create_vm(
            vm_id="test_xcpng_vm", 
            vm_type="xcpng", 
            networked=False, 
            persistent=True, 
            debug_mode=True,  # Enable debug mode for more info
            config=config
        )
        
        print("✅ VM creation object created successfully")
        print("🚀 Attempting to start VM...")
        
        # Try to start the VM
        vm_instance.start()
        
        print("✅ XCP-ng VM started successfully!")
        print("🎉 Test passed - XCP-ng integration is working!")
        
        return True
        
    except Exception as e:
        print(f"❌ XCP-ng VM creation failed: {e}")
        print(f"🐛 Exception type: {type(e).__name__}")
        print(f"🐛 Exception details: {str(e)}")
        print(f"\n🐛 Full traceback:")
        traceback.print_exc()
        
        # Check if it's an authentication or endpoint issue
        error_str = str(e).lower()
        if "404" in error_str or "not found" in error_str:
            print("\n💡 This looks like an API endpoint issue")
            print("💡 The library is trying to access /api/session which doesn't exist")
            print("💡 XCP-ng uses XML-RPC on the root path, not REST API")
        elif "500" in error_str or "internal server error" in error_str:
            print("\n💡 This looks like an XML parsing issue")
            print("💡 The library might be sending malformed XML-RPC requests")
        elif "authentication" in error_str or "401" in error_str:
            print("\n💡 This looks like an authentication issue")
            print("💡 Check your username and password")
        
        return False

def test_basic_vm_fallback():
    """Test basic VM creation as a fallback"""
    print("\n🔄 Testing Basic VM Creation (Fallback)...")
    
    try:
        vm = create_vm("test_basic_vm", vm_type="basic")
        result = vm.execute_string('print("Basic VM test successful")')
        print("✅ Basic VM creation works - library is functional")
        if hasattr(vm, 'cleanup'):
            vm.cleanup()
        return True
    except Exception as e:
        print(f"❌ Basic VM creation also failed: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Update the password fields in this script before running!")
    print("⚠️  Look for 'your_password_here' and replace with actual XCP-ng password")
    print()
    
    # Test XCP-ng VM creation
    xcpng_success = test_xcpng_vm_creation()
    
    if not xcpng_success:
        print("\n" + "=" * 60)
        print("XCP-ng test failed, trying basic VM as sanity check...")
        basic_success = test_basic_vm_fallback()
        
        if basic_success:
            print("✅ Library is working, issue is specific to XCP-ng integration")
        else:
            print("❌ Library has fundamental issues")
    
    print("\n" + "=" * 60)
    print("🏁 Testing complete!")
    
    if xcpng_success:
        print("🎉 XCP-ng integration is working!")
    else:
        print("⚠️  XCP-ng integration needs fixing")
        print("💡 Based on the endpoint tests, the library needs to:")
        print("   1. Use XML-RPC on root path (/) instead of /api/session")
        print("   2. Fix XML formatting for XCP-ng compatibility")
        print("   3. Handle XCP-ng's specific authentication method")
