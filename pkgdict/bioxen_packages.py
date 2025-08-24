#!/usr/bin/env python3
"""
BioXen Package Definitions
Package catalog and environment profiles for the BioXen Lua VM ecosystem.
"""

from pylua_bioxen_vm_lib.utils.curator import Package

# BioXen-specific package collections
BIOXEN_PACKAGES = {
    "bio-utils": Package("bio-utils", category="biology", priority=9,
                        description="Essential biological data processing utilities"),
    "sequence-parser": Package("sequence-parser", category="biology", priority=8,
                              description="DNA/RNA/protein sequence parsing and analysis"),
    "phylo-tree": Package("phylo-tree", category="biology", priority=7,
                         description="Phylogenetic tree construction and analysis"),
    "blast-parser": Package("blast-parser", category="biology", priority=6,
                           description="BLAST output parsing and analysis"),
    "genome-tools": Package("genome-tools", category="biology", priority=7,
                           description="Genome assembly and annotation tools"),
    "protein-fold": Package("protein-fold", category="biology", priority=5,
                           description="Protein structure prediction utilities"),
    "gabby-lua": Package("gabby-lua", category="ai", priority=8,
                        description="AI conversational interface for Lua environments"),
    "lua-radio": Package("lua-radio", category="radio", priority=7,
                        description="Software defined radio functionality for Lua"),
}

# Core system packages that are commonly used across profiles
CORE_PACKAGES = {
    "lua-cjson": Package("lua-cjson", category="core", priority=10,
                        description="Fast JSON parsing and encoding"),
    "luafilesystem": Package("luafilesystem", category="core", priority=9,
                            description="File system operations"),
    "luasocket": Package("luasocket", category="core", priority=9,
                        description="Network support for Lua"),
    "penlight": Package("penlight", category="core", priority=7,
                       description="General-purpose utility libraries"),
    "luaposix": Package("luaposix", category="system", priority=6,
                       description="POSIX system interface"),
}

# Extended packages for specialized use cases
EXTENDED_PACKAGES = {
    "lpeg": Package("lpeg", category="parsing", priority=6,
                   description="Pattern-matching library"),
    "lua-curl": Package("lua-curl", category="network", priority=5,
                       description="HTTP client functionality"),
    "lua-messagepack": Package("lua-messagepack", category="serialization", priority=5,
                              description="MessagePack serialization"),
    "lua-yaml": Package("lua-yaml", category="serialization", priority=4,
                       description="YAML parsing and generation"),
    "lua-term": Package("lua-term", category="terminal", priority=4,
                       description="Terminal control and ANSI colors"),
}

# Combine all packages for easy access
ALL_PACKAGES = {
    **BIOXEN_PACKAGES,
    **CORE_PACKAGES, 
    **EXTENDED_PACKAGES
}