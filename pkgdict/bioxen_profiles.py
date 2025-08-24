#!/usr/bin/env python3
"""
BioXen Environment Profiles
Pre-configured package combinations for different use cases.
"""

# BioXen-specific environment profiles
BIOXEN_PROFILES = {
    "bioxen-minimal": {
        "packages": [
            "lua-cjson", 
            "luafilesystem", 
            "bio-utils"
        ],
        "description": "Minimal BioXen environment with core biological tools",
        "category": "biology"
    },
    "bioxen-standard": {
        "packages": [
            "lua-cjson", 
            "luafilesystem", 
            "luasocket",
            "bio-utils", 
            "sequence-parser", 
            "phylo-tree",
            "gabby-lua"
        ],
        "description": "Standard BioXen environment with common biological analysis tools and AI interface",
        "category": "biology"
    },
    "bioxen-full": {
        "packages": [
            "lua-cjson", 
            "luafilesystem", 
            "luasocket",
            "bio-utils", 
            "sequence-parser", 
            "phylo-tree", 
            "blast-parser", 
            "genome-tools", 
            "protein-fold",
            "gabby-lua",
            "lua-radio",
            "penlight"
        ],
        "description": "Full BioXen environment with all available biological tools, AI interface, and SDR support",
        "category": "biology"
    },
    "bioxen-ai": {
        "packages": [
            "lua-cjson",
            "luafilesystem",
            "luasocket", 
            "gabby-lua",
            "bio-utils",
            "sequence-parser",
            "penlight"
        ],
        "description": "AI-focused BioXen environment with conversational interface and basic bio tools",
        "category": "ai-biology"
    },
    "bioxen-radio": {
        "packages": [
            "lua-cjson",
            "luafilesystem", 
            "luasocket",
            "lua-radio",
            "lua-messagepack",
            "penlight"
        ],
        "description": "Software-defined radio environment for communication protocols",
        "category": "radio"
    }
}

# General-purpose profiles (non-BioXen specific)
GENERAL_PROFILES = {
    "minimal": {
        "packages": [
            "lua-cjson", 
            "luafilesystem"
        ],
        "description": "Minimal Lua environment with basic utilities",
        "category": "general"
    },
    "standard": {
        "packages": [
            "lua-cjson", 
            "luafilesystem", 
            "luasocket",
            "penlight"
        ],
        "description": "Standard Lua environment with common utilities",
        "category": "general"
    },
    "full": {
        "packages": [
            "lua-cjson", 
            "luafilesystem", 
            "luasocket",
            "penlight",
            "lpeg",
            "lua-curl",
            "lua-messagepack",
            "lua-yaml",
            "lua-term",
            "luaposix"
        ],
        "description": "Full-featured Lua environment with extensive library support",
        "category": "general"
    },
    "network": {
        "packages": [
            "lua-cjson",
            "luafilesystem",
            "luasocket", 
            "lua-curl",
            "lua-messagepack",
            "penlight"
        ],
        "description": "Network-focused environment for distributed applications",
        "category": "networking"
    },
    "development": {
        "packages": [
            "lua-cjson",
            "luafilesystem",
            "luasocket",
            "penlight", 
            "lpeg",
            "lua-term",
            "luaposix"
        ],
        "description": "Development environment with debugging and system tools",
        "category": "development"
    }
}

# Combine all profiles
ALL_PROFILES = {
    **BIOXEN_PROFILES,
    **GENERAL_PROFILES
}

# Profile categories for organized display
PROFILE_CATEGORIES = {
    "biology": "🧬 Biological Analysis",
    "ai-biology": "🤖 AI-Enhanced Biology", 
    "radio": "📡 Software Defined Radio",
    "general": "🔧 General Purpose",
    "networking": "🌐 Networking & Communication",
    "development": "💻 Development & Debugging"
}

# Helper functions for profile management
def get_profiles_by_category(category: str) -> dict:
    """Get all profiles in a specific category."""
    return {name: profile for name, profile in ALL_PROFILES.items() 
            if profile.get("category") == category}

def get_profile_package_count(profile_name: str) -> int:
    """Get the number of packages in a profile."""
    profile = ALL_PROFILES.get(profile_name, {})
    return len(profile.get("packages", []))

def list_profile_categories() -> list:
    """Get a list of all available profile categories."""
    categories = set()
    for profile in ALL_PROFILES.values():
        categories.add(profile.get("category", "general"))
    return sorted(categories)