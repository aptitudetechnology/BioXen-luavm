#!/bin/bash

# install_dependencies.sh
# Installation script for pylua-bioxen-vm dependencies
# Supports Ubuntu/Debian, CentOS/RHEL/Fedora, and macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "ubuntu"
        elif command -v yum &> /dev/null; then
            echo "centos"
        elif command -v dnf &> /dev/null; then
            echo "fedora"
        else
            echo "unknown_linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to install Lua on Ubuntu/Debian
install_lua_ubuntu() {
    print_status "Installing Lua and dependencies on Ubuntu/Debian..."
    
    sudo apt update
    sudo apt install -y lua5.4 lua5.4-dev luarocks build-essential
    
    # Create symlink if lua command doesn't exist
    if ! command_exists lua; then
        if command_exists lua5.4; then
            print_status "Creating symlink for lua command..."
            sudo ln -sf /usr/bin/lua5.4 /usr/bin/lua
        fi
    fi
}

# Function to install Lua on CentOS/RHEL
install_lua_centos() {
    print_status "Installing Lua and dependencies on CentOS/RHEL..."
    
    # Enable EPEL repository for additional packages
    sudo yum install -y epel-release
    sudo yum install -y lua lua-devel luarocks gcc gcc-c++ make
}

# Function to install Lua on Fedora
install_lua_fedora() {
    print_status "Installing Lua and dependencies on Fedora..."
    
    sudo dnf install -y lua lua-devel luarocks gcc gcc-c++ make
}

# Function to install Lua on macOS
install_lua_macos() {
    print_status "Installing Lua and dependencies on macOS..."
    
    if ! command_exists brew; then
        print_error "Homebrew not found. Please install Homebrew first:"
        print_error "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    brew install lua luarocks
}

# Function to install LuaSocket
install_luasocket() {
    print_status "Installing LuaSocket..."
    
    if command_exists luarocks; then
        sudo luarocks install luasocket
    else
        print_error "LuaRocks not found. Cannot install LuaSocket."
        return 1
    fi
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check Lua
    if command_exists lua; then
        LUA_VERSION=$(lua -v 2>&1 | head -n1)
        print_success "Lua installed: $LUA_VERSION"
    else
        print_error "Lua not found in PATH"
        return 1
    fi
    
    # Check LuaRocks
    if command_exists luarocks; then
        LUAROCKS_VERSION=$(luarocks --version 2>&1 | head -n1)
        print_success "LuaRocks installed: $LUAROCKS_VERSION"
    else
        print_warning "LuaRocks not found in PATH"
    fi
    
    # Check LuaSocket
    if lua -e "require('socket'); print('LuaSocket test successful')" 2>/dev/null; then
        print_success "LuaSocket installed and working"
    else
        print_error "LuaSocket not working properly"
        return 1
    fi
    
    print_success "All dependencies verified successfully!"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found, installing pylua-bioxen-vm directly..."
        pip install pylua-bioxen-vm
    fi
}

# Function to run test
run_test() {
    print_status "Running installation test..."
    
    if [[ -f "test_pylua-bioxen-vm.py" ]]; then
        python3 test_pylua-bioxen-vm.py
    else
        print_warning "test_pylua-bioxen-vm.py not found, skipping test"
    fi
}

# Main installation function
main() {
    print_status "Starting pylua-bioxen-vm dependency installation..."
    echo
    
    # Detect operating system
    OS=$(detect_os)
    print_status "Detected OS: $OS"
    echo
    
    # Install based on OS
    case $OS in
        "ubuntu")
            install_lua_ubuntu
            ;;
        "centos")
            install_lua_centos
            ;;
        "fedora")
            install_lua_fedora
            ;;
        "macos")
            install_lua_macos
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            print_error "Please install Lua and LuaSocket manually:"
            print_error "  - Lua interpreter (lua)"
            print_error "  - LuaRocks package manager"
            print_error "  - LuaSocket library (luarocks install luasocket)"
            exit 1
            ;;
    esac
    
    echo
    
    # Install LuaSocket
    if ! install_luasocket; then
        print_error "Failed to install LuaSocket"
        exit 1
    fi
    
    echo
    
    # Install Python dependencies
    install_python_deps
    
    echo
    
    # Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed"
        exit 1
    fi
    
    echo
    
    # Run test if available
    run_test
    
    echo
    print_success "Installation complete! You can now use pylua-bioxen-vm."
    echo
    print_status "Quick test command:"
    echo "  python3 -c \"from pylua_bioxen_vm import VMManager; print('Import successful!')\""
}

# Help function
show_help() {
    echo "pylua-bioxen-vm dependency installer"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --verify-only  Only verify existing installation"
    echo "  --no-test      Skip running the test after installation"
    echo
    echo "This script will install:"
    echo "  - Lua interpreter"
    echo "  - LuaRocks package manager"
    echo "  - LuaSocket library"
    echo "  - Python dependencies from requirements.txt"
    echo
    echo "Supported systems:"
    echo "  - Ubuntu/Debian (apt)"
    echo "  - CentOS/RHEL (yum)"
    echo "  - Fedora (dnf)"
    echo "  - macOS (brew)"
}

# Parse command line arguments
VERIFY_ONLY=false
NO_TEST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --no-test)
            NO_TEST=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if running with verify-only flag
if [[ "$VERIFY_ONLY" == true ]]; then
    print_status "Verification mode - checking existing installation..."
    echo
    verify_installation
    exit $?
fi

# Run main installation
main

# Skip test if --no-test flag is provided
if [[ "$NO_TEST" == true ]]; then
    print_status "Skipping test as requested"
fi