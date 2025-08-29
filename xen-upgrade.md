## Core Dependencies:

1. **libvirt Python bindings** - Primary library for managing Xen VMs
2. **libvirt-dev** - Development headers for libvirt
3. **xen-tools** - Xen management tools and utilities
4. **xen-hypervisor** - Xen hypervisor itself

## Python Packages:

```bash
# Essential packages
pip install libvirt-python
pip install python-xenapi

# Optional but recommended
pip install libxml2-python  # For XML configuration handling
pip install python-params  # For advanced configuration management
```